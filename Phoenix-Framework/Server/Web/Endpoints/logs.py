from Database import LogEntryModel, Session
from flask import (Blueprint, jsonify,
                   render_template, request)
from Utils.web import (admin, authorized, generate_response, get_current_user,
                       get_messages)

ENDPOINT = "logs"
logs_bp = Blueprint(ENDPOINT, __name__, url_prefix="/logs")


@logs_bp.route("/", methods=["GET"])
@authorized
def get_logs():
    use_json = request.args.get("json", "").lower() == "true"
    current_user = get_current_user()
    logentry_query = Session.query(LogEntryModel)
    logs: list[LogEntryModel] = logentry_query.all()
    for log in logs:
        log.seen_by_user(current_user)
    Session.commit()
    opened_log = logentry_query.filter_by(id=request.args.get("open")).first()
    if use_json:
        return jsonify({"status": "success", ENDPOINT: [log.to_dict() for log in logs]})
    return render_template("logs.j2", user=current_user, logs=logs, opened_log=opened_log, messages=get_messages())


@logs_bp.route("/<string:id>/clear", methods=["POST"])
@admin
def post_clear_devices(id: str = "all"):
    count = 0
    if id == "all":
        for log in Session.query(LogEntryModel).all():
            if not log.unseen_users:
                count += 1
                Session.delete(log)
    else:
        for log in Session.query(LogEntryModel).filter_by(id=id).all():
            if not log.unseen_users:
                count += 1
                Session.delete(log)
    LogEntryModel.log("info", "logs", f"Cleared {count} logs.", Session, get_current_user())
    Session.commit()
    return generate_response("success", f"Cleared {count} log entries.", "logs")
