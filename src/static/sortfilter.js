$(document).ready(function() {
    var sort_el = $('.sortfilter select').eq(0);
    var filter_el = $('.sortfilter select').eq(1);
    
    function update() {
        window.location = '?sort=' + sort_el.val() + '&filter=' + filter_el.val();
    };
    
    sort_el.change(update);
    filter_el.change(update);

})

