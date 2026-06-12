from datetime import datetime

from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import ScoreReview

reviews_bp = Blueprint("reviews", __name__, url_prefix="/api/reviews")

VALID_STATUSES = ["待审核", "审核中", "已完成", "已驳回"]
VALID_RESULTS = ["维持原成绩", "成绩更正"]


@reviews_bp.get("")
def list_reviews():
    status = request.args.get("status")
    query = ScoreReview.query.order_by(ScoreReview.created_at.desc())
    if status:
        query = query.filter_by(status=status)
    return jsonify([item.to_dict() for item in query.all()])


@reviews_bp.post("")
def create_review():
    payload = request.get_json() or {}
    required = ["studentName", "subject", "originalScore", "reason"]
    missing = [field for field in required if payload.get(field) in (None, "")]
    if missing:
        return jsonify({"message": f"缺少字段：{', '.join(missing)}"}), 400

    review = ScoreReview(
        student_name=payload["studentName"].strip(),
        subject=payload["subject"],
        original_score=int(payload["originalScore"]),
        reason=payload["reason"].strip(),
        status="待审核",
    )
    db.session.add(review)
    db.session.commit()
    return jsonify(review.to_dict()), 201


@reviews_bp.patch("/<int:review_id>")
def update_review(review_id):
    review = ScoreReview.query.get_or_404(review_id)
    payload = request.get_json() or {}

    if "status" in payload:
        if payload["status"] not in VALID_STATUSES:
            return jsonify({"message": "无效复核状态"}), 400
        review.status = payload["status"]

    if "result" in payload:
        if payload["result"] not in VALID_RESULTS:
            return jsonify({"message": "无效复核结果"}), 400
        review.result = payload["result"]
        review.reviewed_at = datetime.utcnow()
        review.status = "已完成"

    db.session.commit()
    return jsonify(review.to_dict())
