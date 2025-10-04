from flask import jsonify


class APIResponse:
    @staticmethod
    def success(data=None, message="Success", status_code=200):
        """Standard success response"""
        response = {"success": True}
        if message:
            response["message"] = message
        if data:
            (
                response.update(data)
                if isinstance(data, dict)
                else response.update({"data": data})
            )
        return jsonify(response), status_code

    @staticmethod
    def error(message="Error", details=None, status_code=400):
        """Standard error response"""
        response = {"success": False, "error": message}
        if details:
            response["details"] = details
        return jsonify(response), status_code

    @staticmethod
    def unauthorized(message="Unauthorized"):
        """401 response"""
        return APIResponse.error(message, status_code=401)

    @staticmethod
    def forbidden(message="Forbidden"):
        """403 response"""
        return APIResponse.error(message, status_code=403)

    @staticmethod
    def not_found(message="Resource not found"):
        """404 response"""
        return APIResponse.error(message, status_code=404)
