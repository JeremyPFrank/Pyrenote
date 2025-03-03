import sqlalchemy as sa
from sqlalchemy import or_
from sqlalchemy.sql.expression import false, true, null
import uuid
from random import randint
from flask import jsonify, flash, redirect, url_for, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.urls import url_parse
from .projects import give_users_examples
from backend import app, db
from backend.models import Project, User, Data, Segmentation
from .helper_functions import remove_previously_viewed_clips
from . import api

@api.route("next_clip/next_rec/project/<int:project_id>/data/<int:data_id>",
           methods=["GET"])
@api.route("/next_clip/project/<int:project_id>/data/<int:data_id>",
           methods=["GET"])
@jwt_required
def getNextClip(project_id, data_id):
    identity = get_jwt_identity()
    app.logger.info(request.path)
    url = request.path
    active = request.args.get("active", "pending", type=str)
    project = Project.query.get(project_id)
    app.logger.info("HEY HYE HEY RIGHT HERE")
    app.logger.info(active)

    segmentations = None
    if(project.is_iou and active =="pending"):
        exit_info, exit_code = getNextViaConfidence(project_id, data_id, request, identity)
        app.logger.info(exit_info)
        app.logger.info(exit_code)
        return exit_info, exit_code
    elif(project.is_iou):
        segmentations = db.session.query(Segmentation.data_id).distinct().filter_by(created_by=identity["username"]).subquery()
    app.logger.info(url)    
    if (url.startswith("/api/next_clip/next_rec/project/")):
        
        return getNextReccomendedData(project_id, data_id, request, identity, segmentations=segmentations)
    else:
        return getNextClipFromNextButton(project_id, data_id, request, identity, segmentations=segmentations)



def getNextViaConfidence(project_id, data_id, request, identity):
    app.logger.info("USING THIS ONE WITH CONFIDENCE")
    identity = get_jwt_identity()
    active = "pending"
    dataReview = None
    dataPending = None
    key = identity["username"]
    project = Project.query.get(project_id)
    THRESHOLD = project.threshold
    MAX_USERS = project.max_users
    app.logger.info("THRESHOLD")
    app.logger.info(THRESHOLD)
    app.logger.info(MAX_USERS)

    try:
        request_user = User.query.filter_by(username=identity["username"]
                                            ).first()
        segmentations = db.session.query(Segmentation.data_id).distinct().filter_by(created_by=identity["username"]).subquery()
        data = None
        try:
            dataPendingList = list(
                db.session.query(Data)
                .filter(Data.project_id == project_id)
                .filter(or_(Data.id.notin_(segmentations), Data.users_reviewed[key] == null()))
                .filter(Data.confidence < THRESHOLD)
                .filter(Data.num_reviewed < MAX_USERS)
                .filter(Data.id != data_id)
                .distinct()
                .all()
            )

            app.logger.info(dataPendingList)
            item = randint(0, len(dataPendingList) - 1)
            app.logger.info(item)
            dataPending = dataPendingList[item]
        except Exception as e:
            app.logger.info("ERROR")
            app.logger.info(e)
            dataPending = None
        app.logger.info("PENDING DATA")
        app.logger.info(dataPending)
        data = dataPending
        app.logger.info("FINAL DATA POINT")
        app.logger.info(data)
        response = list(
            [
                {
                    "data_id": data.id,
                    "filename": data.filename,
                    "original_filename": data.original_filename,
                    "created_on": data.created_at.strftime("%B %d, %Y"),
                    "is_marked_for_review": data.is_marked_for_review,
                    "number_of_segmentations": len(data.segmentations),
                    "sampling_rate": data.sampling_rate,
                    "clip_length": data.clip_length,
                }
            ]
        )
        app.logger.info("RETURN?")
        app.logger.info(response)
        return (
            jsonify(
                data=response,
                data_id=data.id,
                active=active,
            ),
            200,
        )
    except Exception as e:
        message = "Error fetching all data points"
        app.logger.error(message)
        app.logger.error(e)
        return jsonify(message=message), 501
    return 100

def getNextClipFromNextButton(project_id, data_id, request, identity, segmentations=None):
    identity = get_jwt_identity()
    # page = request.args.get("page", 1, type=int)
    active = request.args.get("active", "completed", type=str)

    try:
        app.logger.info("made it here")
        request_user = User.query.filter_by(username=identity["username"]
                                            ).first()
        app.logger.info("made it here")
        project = Project.query.get(project_id)
        THRESHOLD = project.threshold
        MAX_USERS = project.max_users
        app.logger.info("made it here")
        if request_user not in project.users:
            return jsonify(message="Unauthorized access!"), 401
        app.logger.info("made it here")
        if (segmentations == None):
            segmentations = db.session.query(Segmentation.data_id
                                            ).distinct().subquery()
        # Lets set big id to the {username.idenity, username.id}
        # this would make it fast but aslo render serval data points
        data = {}
        # print(Data.assigned_user_id)
        # for key in Data.assigned_user_id:
        #    if request_user.id == Data.assigned_user_id[key]:
        #        big_key = key
        #        print(big_key, key)
        app.logger.info("made it here")
        data["pending"] = (
            db.session.query(Data)
            .filter(or_(Data.sample != true(), Data.sample == null()))
            .filter(Data.project_id == project_id)
            .filter(Data.id.notin_(segmentations))
            .distinct()
            .order_by(Data.last_modified.desc())
        )

        data["marked_review"] = Data.query.filter_by(
            project_id=project_id,
            is_marked_for_review=True,
        ).order_by(Data.last_modified.desc())

        data["all"] = Data.query.filter_by(
            project_id=project_id
        ).order_by(Data.last_modified.desc())

        data["completed"] = (
            db.session.query(Data)
            .filter(or_(Data.sample != true(), Data.sample == null()))
            .filter(Data.project_id == project_id)
            .filter(Data.id.in_(segmentations))
            .distinct()
            .order_by(Data.last_modified.desc())
        )

        data["retired"] = (
            db.session.query(Data)
            .filter(or_(Data.sample != true(), Data.sample == null()))
            .filter(or_(request_user.id == Data.assigned_user_id[identity["username"]], Data.assigned_user_id[identity["username"]] == null()))
            .filter(Data.project_id == project_id)
            .filter(or_(
                Data.num_reviewed >= MAX_USERS,
                Data.confidence >= THRESHOLD,
            ))
            .distinct()
            .order_by(Data.last_modified.desc())
        )
        app.logger.info(active)
        page = -1
        test_page = 1
        while (page == -1):
            paginated_data = data[active].paginate(test_page, 10, False)
            next = paginated_data.next_num if paginated_data.has_next else None
            prev = paginated_data.prev_num if paginated_data.has_prev else None
            count = 0
            data_subset = paginated_data.items
            for data_point in data_subset:
                if (data_point.id == data_id):
                    next_data = None
                    app.logger.info(count)
                    app.logger.info(len(data_subset))
                    app.logger.info((len(data_subset) == count + 1))
                    if (len(data_subset) == count + 1 and next):
                        next_data = data[active].paginate(test_page + 1, 10,
                                                          False).items[0]
                    elif (len(data_subset) > count + 1):
                        next_data = data_subset[count + 1]
                        app.logger.info(next_data)
                        app.logger.info("yikes")
                    else:
                        return jsonify(msg="no more data"), 202
                    return (
                        jsonify(
                            data=next_data.to_dict(),
                            data_id=next_data.id,
                            next_page=next,
                            prev_page=prev,
                            page=test_page,
                            active=active,
                        ),
                        200,
                    )
                count += 1
            if (next is not None):
                test_page += 1
            else:
                next_data = data[active].paginate(1, 1, False).items[0]
                pd = data[active].paginate(1, 10, False)
                next = pd.next_num if paginated_data.has_next else None
                prev = pd.prev_num if paginated_data.has_prev else None
                return (
                        jsonify(
                            data=next_data.to_dict(),
                            data_id=next_data.id,
                            next_page=next,
                            prev_page=prev,
                            page=test_page,
                            active=active,
                        ),
                        200,
                    )
    except Exception as e:
        message = "Error fetching all data points"
        app.logger.error(message)
        app.logger.error(e)
        return jsonify(message=message), 501
    message = f"Error data value `{data_id}` not in project"
    app.logger.error(message)
    return jsonify(message=message), 404



def getNextReccomendedData(project_id, data_id, request, identity, segmentations=None):
    app.logger.info("USING THIS ONE")
    identity = get_jwt_identity()
    active = "pending"

    try:
        request_user = User.query.filter_by(username=identity["username"]
                                            ).first()
        if (segmentations == None):
            segmentations = db.session.query(Segmentation.data_id
                                            ).distinct().subquery()
        data = None
        try:
            dataPendingList = list(
                db.session.query(Data)
                .filter(Data.project_id == project_id)
                .filter(Data.id != data_id)
                .filter(Data.id.notin_(segmentations))
                .distinct()
                .all()
            )
            dataPending = dataPendingList[randint(0, len(dataPendingList) - 1)]
        except Exception:
            dataPending = None

        key = identity["username"]
        try:
            dataReviewList = list(
                    db.session.query(Data)
                    .filter(Data.project_id == project_id)
                    .filter(Data.is_marked_for_review)
                    .filter(Data.id.in_(segmentations))
                    .filter(Data.id != data_id)
                    .filter(Data.assigned_user_id[key] != request_user.id)
                    .distinct()
                    .all()
                )
            dataReview = dataReviewList[randint(0, len(dataReviewList) - 1)]
        except Exception:
            dataReview = None

        review_chance = (dataPending is None or randint(0, 5) == 0)
        app.logger.info(dataReview)
        if (dataPending is None and dataReview is None):
            return (405)
        elif (review_chance and dataReview is not None):
            data = dataReview
            active = "marked_review"
        else:
            data = dataPending
        response = list(
            [
                {
                    "data_id": data.id,
                    "filename": data.filename,
                    "original_filename": data.original_filename,
                    "created_on": data.created_at.strftime("%B %d, %Y"),
                    "is_marked_for_review": data.is_marked_for_review,
                    "number_of_segmentations": len(data.segmentations),
                    "sampling_rate": data.sampling_rate,
                    "clip_length": data.clip_length,
                }
            ]
        )
        return (
            jsonify(
                data=response,
                data_id=data.id,
                active=active,
            ),
            200,
        )
    except Exception as e:
        message = "Error fetching all data points"
        app.logger.error(message)
        app.logger.error(e)
        return jsonify(message=message), 501


@api.route(
 "/current_user/unknown/projects/<int:project_id>/data/<int:data_value>",
 methods=["GET"]
)
@jwt_required
def get_next_data_unknown(project_id, data_value):
    identity = get_jwt_identity()
    # page = request.args.get("page", 1, type=int)
    active = request.args.get("active", "completed", type=str)

    try:
        request_user = User.query.filter_by(username=identity["username"]
                                            ).first()
        project = Project.query.get(project_id)
        project = Project.query.get(project_id)

        if request_user not in project.users:
            return jsonify(message="Unauthorized access!"), 401

        segmentations = db.session.query(Segmentation.data_id
                                         ).distinct().subquery()
        # Lets set big id to the {username.idenity, username.id}
        # this would make it fast but aslo render serval data points
        data = {}
        big_key = identity["username"]
        # print(Data.assigned_user_id)
        # for key in Data.assigned_user_id:
        #    if request_user.id == Data.assigned_user_id[key]:
        #        big_key = key
        #        print(big_key, key)
        data["pending"] = (
            db.session.query(Data)
            .filter(or_(Data.sample != true(), Data.sample == null()))
            .filter(Data.project_id == project_id)
            .filter(Data.id.notin_(segmentations))
            .distinct()
            .order_by(Data.last_modified.desc())
        )

        data["completed"] = (
            db.session.query(Data)
            .filter(or_(Data.sample != true(), Data.sample == null()))
            .filter(Data.project_id == project_id)
            .filter(Data.id.in_(segmentations))
            .distinct()
            .order_by(Data.last_modified.desc())
        )

        active = "unknown"
        if (active != "pending"):
            for data_pt in data["completed"]:
                if data_pt.id == data_value:
                    active = "completed"
                    break
            if (active == "unknown"):
                active = "pending"
            app.logger.info(active)

        page = -1
        test_page = 1
        while (page == -1):
            paginated_data = data[active].paginate(test_page, 10, False)
            next = paginated_data.next_num if paginated_data.has_next else None
            prev = paginated_data.prev_num if paginated_data.has_prev else None
            for data_point in paginated_data.items:
                if (data_point.id == data_value):
                    response = list(
                        [
                            {
                                "data_id": data_point.id,
                            }
                            for data_point in paginated_data.items
                        ]
                    )
                    return (
                        jsonify(
                            data=response,
                            next_page=next,
                            prev_page=prev,
                            page=test_page,
                            active=active,
                        ),
                        200,
                    )
            if (next is not None):
                test_page += 1
    except Exception as e:
        message = "Error fetching all data points"
        app.logger.error(message)
        app.logger.error(e)
        return jsonify(message=message), 501
    message = f"Error data value `{data_value}` not in project"
    app.logger.error(message)
    return jsonify(message=message), 404
