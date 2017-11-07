from flask import render_template, request, jsonify
from . import main

#它向 Web 服务客户端发送 JSON 格式响应，除此之外都发送 HTML 格式响应
@main.app_errorhandler(403)
def forbidden(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return render_template('403.html'), 403

@main.app_errorhandler(404)
def page_not_found(e):
    #处理 404 和 500 状态码时会有点小麻烦，因为这两个错误是由 Flask 自己生成的，而且一
    #般会返回 HTML 响应，这很可能会让 API 客户端困惑。
    #浏览器一般不限制响应的格式，所以只为接受 JSON 格式而不接受 HTML 格式的客户端生成 JSON 格式响应
    if request.accept_mimetypes.accept_json and \
           not request.accept_mimetypes.accept_html:
#需要包含 JSON 的响应可以使用 Flask 提供的辅助函数jsonify()从Python字典中生成
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        #JSON 格式响应
        print('accept_mimetypes' in dir(request))
        return response
    # HTML 格式响应
    
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('500.html'), 500
