$('#navbarSupportedContent .navbar-nav li').on('click', function () {
    $('#navbarSupportedContent .navbar-nav').find('li.active').removeClass('active');
    $(this).parent('li').addClass('active');
});