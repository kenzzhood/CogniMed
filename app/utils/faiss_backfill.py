"""
Script to backfill the FAISS index with all existing posts from the database.
Run this script once to initialize the vector index for semantic search.
"""

import sys
import os
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.db.db_schema import Post as PostModel
from app.utils.faiss_utils import build_faiss_index


def main():
    print("[FAISS Backfill] Starting backfill of FAISS index from all posts...")
    db_session: Session = SessionLocal()
    posts = db_session.query(PostModel).all()
    db_session.close()
    texts = []
    metadatas = []
    for post in posts:
        if post.text:
            texts.append(post.text)
            metadatas.append(
                {
                    "post_id": post.post_id,
                    "user_id": post.user_id,
                    "created_time": (
                        str(post.created_time) if post.created_time else None
                    ),
                }
            )
    if not texts:
        print("[FAISS Backfill] No posts found. Nothing to index.")
        return
    build_faiss_index(texts, metadatas)
    print(f"[FAISS Backfill] Indexed {len(texts)} posts into FAISS vector store.")


if __name__ == "__main__":
    main()
