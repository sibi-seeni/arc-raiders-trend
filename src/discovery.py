import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from googleapiclient.discovery import build
from sqlalchemy.orm import Session
from .database import SessionLocal, Video, CollectionState

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

KEYWORDS = [
    "Arc Raiders", "ARC RAIDERS", "arc raiders",
    "#arcraiders", "#ArcRaiders", "#ARCRAIDERS",
    "Arc raiders", "#Arcraiders"
]

BACKFILL_START = datetime(2021, 12, 9)
WINDOW_DAYS = 90


def get_youtube_client():
    return build("youtube", "v3", developerKey=API_KEY)

def title_matches(title):
    title_lower = title.lower()
    return any(k.lower() in title_lower for k in KEYWORDS)

def search_new_videos():
    youtube = get_youtube_client()
    db: Session = SessionLocal()

    added_this_session = set()

    for keyword in KEYWORDS:

        state = db.query(CollectionState).filter_by(keyword=keyword).first()

        if not state:
            # First run starts from today
            cursor = datetime.utcnow()
            state = CollectionState(keyword=keyword, last_search_time=cursor)
            db.add(state)
            db.commit()
        else:
            cursor = state.last_search_time

        # Move backwards 90 days each run
        published_before = cursor
        published_after = max(BACKFILL_START, cursor - timedelta(days=WINDOW_DAYS))

        print(
            f"Searching '{keyword}' between "
            f"{published_after} and {published_before}"
        )

        next_page_token = None

        while True:

            request = youtube.search().list(
                q=keyword,
                part="snippet",
                type="video",
                order="date",
                videoCategoryId="20",
                maxResults=50,
                pageToken=next_page_token,
                publishedAfter=published_after.strftime('%Y-%m-%dT%H:%M:%SZ'),
                publishedBefore=published_before.strftime('%Y-%m-%dT%H:%M:%SZ')
            )

            response = request.execute()

            for item in response.get("items", []):

                video_id = item["id"]["videoId"]
                title = item["snippet"]["title"]

                # ADD THIS FILTER HERE
                if not title_matches(title):
                    continue
                
                # UPDATED LOGIC: Check both DB and the local session set
                if video_id not in added_this_session:

                    exists = db.query(Video).filter_by(video_id=video_id).first()

                    if not exists:
                        new_video = Video(
                            video_id=video_id,
                            title=item["snippet"]["title"],
                            description=item["snippet"]["description"],
                            channel_id=item["snippet"]["channelId"],
                            published_at=datetime.strptime(
                                item["snippet"]["publishedAt"],
                                '%Y-%m-%dT%H:%M:%SZ'
                            ),
                            keyword_matched=keyword
                        )

                        db.add(new_video)
                        added_this_session.add(video_id)

            next_page_token = response.get("nextPageToken")

            if not next_page_token:
                break

        # -------- NEW: RECENT VIDEO DISCOVERY --------
        recent_after = datetime(2025, 1, 1).strftime('%Y-%m-%dT%H:%M:%SZ')
        recent_before = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        print(f"Searching RECENT data for '{keyword}' ({recent_after} to {recent_before})...")

        next_page_token = None

        while True:
            request = youtube.search().list(
                q=keyword,
                part="snippet",
                type="video",
                order="date",  # date works better for recent discovery
                publishedAfter=recent_after,
                publishedBefore=recent_before,
                videoCategoryId="20",
                maxResults=50,
                pageToken=next_page_token
            )

            response = request.execute()

            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                title = item["snippet"]["title"]

                # ADD HERE ALSO
                if not title_matches(title):
                    continue

                if video_id not in added_this_session:
                    exists = db.query(Video).filter_by(video_id=video_id).first()

                    if not exists:
                        new_video = Video(
                            video_id=video_id,
                            title=item["snippet"]["title"],
                            description=item["snippet"]["description"],
                            channel_id=item["snippet"]["channelId"],
                            published_at=datetime.strptime(
                                item["snippet"]["publishedAt"],
                                '%Y-%m-%dT%H:%M:%SZ'
                            ),
                            keyword_matched=keyword
                        )

                        db.add(new_video)
                        added_this_session.add(video_id)

            next_page_token = response.get("nextPageToken")

            if not next_page_token:
                break

        # Commit after each keyword to clear the memory and save progress
        state.last_search_time = datetime.utcnow()
        db.commit()

    db.close()
    print("Discovery Phase Complete.")


if __name__ == "__main__":
    search_new_videos()
    