moment.locale("en");
function flask_moment_render(elem) {
    $(elem).text(eval('moment("' + $(elem).data('timestamp') + '").' + $(elem).data('format') + ';'));
    $(elem).removeClass('flask-moment').show();
}
function flask_moment_render_all() {
    $('.flask-moment').each(function() {
        flask_moment_render(this);
        if ($(this).data('refresh')) {
            (function(elem, interval) { setInterval(function() { flask_moment_render(elem) }, interval); })(this, $(this).data('refresh'));
        }
    })
}
$(document).ready(function() {
    flask_moment_render_all();
});


//关闭click.bs.dropdown.data-api事件，使顶级菜单可点击
$(document).off('click.bs.dropdown.data-api');
//自动展开
$('.nav .dropdown').mouseenter(function(){
 $(this).addClass('open');
});
//自动关闭
$('.nav .dropdown').mouseleave(function(){
 $(this).removeClass('open');
});