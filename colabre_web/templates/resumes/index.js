$(function(){

	var q = $("#search-term").val();

	// load content and toggle visibility
	$(document).on("click", ".resume-wrapper-summary button.show-details" , function(){

		resId = $(this).attr("resume-id");

		req = $.ajax({
			url: '/curriculos/parcial/detalhar/' + resId + '/' + q.replace('#', '%23') + '/',
			type: 'get',
			complete: function()
			{

			},
			success: function(data)
			{
				respResId = req.getResponseHeader('resume-id')
				_this = $("div.resume-wrapper-summary[resume-id=" + respResId + "]");

				details = _this.children("div.resume-details");

				_this.removeClass("resume-wrapper-summary")
					.addClass("resume-wrapper-details wrapper-expanded");

				details.empty();
				details.html(data);
				
				details.show('fast', function(){});
			},
			error: function(a, b, error)
			{
				alert('Desculpe-nos, fizemos alguma coisa errada: ' + error);
			}
		});
	});

	// toggle visibility after content is loaded...
	$(document).on("click", ".resume-wrapper-details button.show-details" , function() {
		_this = $(this).parent('.resume-wrapper-details');
		details = _this.children("div.resume-details");
		details.toggle({
			duration: 'fast',
			complete: function(){
				_this.toggleClass('wrapper-expanded wrapper-contracted');
			}
		});
	});
	
	$(document).on("click", ".resume a" , function(e) {
		e.stopPropagation();
	});

	var page = 1;

	// avoid resending the same request twice when page is scrolled all the way down
	var lock = false;

	var display_result = function(result)
	{
		$("#search-loading-img").hide();
		$("#search-loading").hide();
		$("#search-search-info").show();
		$("#search-result").html(result);
		page++;
	};

	var display_result_append = function(result)
	{
		$("#search-loading-img").hide();
		$("#search-loading").hide();
		$("#search-search-info").show();
		$("#search-result").append(result);
		page++;
		lock = false;
	};

	var send_search = function(callback)
	{
		segments = [];
		_locations = [];
		$(".segment-item:checked").each(function(){
			segments.push($(this).val());
		});
		$(".city-item:checked").each(function(){
			_locations.push($(this).val());
		});
		data = {
			term: q,
			segments: segments.join("-"),
			cities: _locations.join("-"),
			page: page,
			csrfmiddlewaretoken: '{{ csrf_token }}'
		};
		$("#search-loading-img").show();
		$("#search-search-info").hide();
		search("/curriculos/parcial/buscar/", 'post', data, callback);
	};

	$(".filter-control").bind('change select', function() {
		page = 1;
		send_search(display_result);
	});

	$("#btn-search").click(function(){
		q = $("#search-term").val();
		page = 1;
		send_search(display_result);
	});

	$("#search-term").keyup(function(e){
		code = e.which ? e.which : e.keyCode;
		q = $(this).val();
		if (code == 13)
		{
			page = 1;
			send_search(display_result);
		}
	});

	$(window).scroll(function(){
		if(!lock && $(window).scrollTop() == $(document).height() - $(window).height())
		{
			if ($("#stop_request_on_scroll").size() > 0)
				return;

			lock = true;
			$("#search-loading").show();
			send_search(display_result_append);
		}
	});

	$("#search-term").focus();

	send_search(display_result);
	
	$(document).on("click", ".profile-name, .contact-form", function(e){
		e.stopPropagation();
	});
			
	$(document).on("click", ".contact-form-opener", function(){
		user_id = $(this).attr("user-id");
		form = $("#contact-form-" + user_id);
		_this = ($(this));
		form.toggle('fast', function(){
			if ($(this).is(":visible"))
			{
				_this.html(_this.html().replace("◄", "▼"));
			}
			else
			{
				_this.html(_this.html().replace("▼", "◄"));
			}	
		});
	});
	
});