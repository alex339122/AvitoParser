$('body').mousemove(function (e) {
    var moveX = (e.pageX * -1/40);
    var moveY = (e.pageY * -1/40);
    $('.bg').css('background-position', moveX + 'px ' + moveY + 'px');
})

var a = window.location.href.split('/')
if(a[a.length-1] == 'viewresults') {
    $('.bg').css({'position':'fixed', 'width':'100%'});
    $('body').unbind('mousemove');
    $('.authorization-button').css({'display':'none'})
}


// --- preloader ---
$('#pushme').on('click', function () {
                                $('.preloader').addClass('active');
                            });


//-------- Ajax ------ viewresults ------------//


$(window).scroll(function() {
    if($(window).scrollTop() + $(window).height() >= $(document).height()) {
        $.get("/viewresultsajax", function (data) {
            if(!data) {
                $(window).unbind('scroll');
            }
            $('tbody').append(data);
        });
    }
});


//--------Translit--------entry page------------//

var ru = ['Я','я','Ю','ю','Ч','ч','Ш','ш','Щ','щ','Ж','ж','А','а','Б','б','В','в','Г','г','Д','д','Е','е','Ё','ё','З','з','И','и','Й','й','К','к','Л','л','М','м','Н','н', 'О','о','П','п','Р','р','С','с','Т','т','У','у','Ф','ф','Х','х','Ц','ц','Ы','ы','Ь','ь','Ъ','ъ','Э','э'];
var en = ['Ya','ya','Yu','yu','Ch','ch','Sh','sh','Sh','sh','Zh','zh','A','a','B','b','V','v','G','g','D','d','E','e','E','e','Z','z','I','i','J','j','K','k','L','l','M','m','N','n', 'O','o','P','p','R','r','S','s','T','t','U','u','F','f','H','h','C','c','Y','y','`','`','\'','\'','E', 'e'];

function translit(text) {
    var splitedText = text.split('');
    for(var i=0; i<splitedText.length; i++) {
        var index = ru.indexOf(splitedText[i]);
        if(index >= 0) {
            splitedText[i] = en[index];
        }
    }
    result = splitedText.join('');
    return result.toUpperCase();
}

$('#city_input').on('keyup', function (e) {
    var text = e.target.value;
    e.target.value = translit(text);
});