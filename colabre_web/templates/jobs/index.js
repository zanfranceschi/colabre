$(function(){

	var q = $("#search-term").val();

	// load content and toggle visibility
	$(document).on("click", ".job-wrapper-summary button.show-details" , function(){

		jobId = $(this).attr("job-id");

		req = $.ajax({
			url: '/vagas/parcial/detalhar/' + jobId + '/' + q.replace('#', '%23') + '/',
			type: 'get',
			beforeSend: function()
			{
				$("img[job-id='" + jobId + "'], button[job-id='" + jobId + "']").toggle('fast');
			},
			complete: function(x, status)
			{

			},
			success: function(data)
			{
				respJobId = req.getResponseHeader('job-id')
				_this = $("div.job-wrapper-summary[job-id=" + respJobId + "]");

				details = _this.children("div.job-details");

				_this.removeClass("job-wrapper-summary")
					.addClass("job-wrapper-details wrapper-expanded");

				$("button.show-details[job-id='"+respJobId+"']").text("- detalhes");
				$("img[job-id='" + respJobId + "'], button[job-id='" + respJobId + "']").toggle('fast');

				details.empty();
				details.html(data);
				viewsReq = $.ajax({
					url: '/vagas/parcial/detalhar/visualizacoes/' + jobId + '/',
					type: 'get',
					error: function(a, b, error)
					{
						alert('Desculpe-nos, fizemos algo errado: ' + error);
					},
					success: function(c)
					{
						viewsRespJobId = viewsReq.getResponseHeader('job-id')

						viewsDiv = $(".job_view_count[job-details-views-id=" + viewsRespJobId + "]");

						if (c == '0')
						{
							viewsDiv.html('Esta é a primeira visualização desta vaga!');
						}
						else if (c == '1')
						{
							viewsDiv.html('Esta vaga já foi vista <b>1</b> vez.');
						}
						else
						{
							viewsDiv.html('Esta vaga já foi vista <b>' + c + '</b> vezes.');
						}
					}
				});

				details.show('fast', function(){});
			},
			error: function(a, b, error)
			{
				console.log('error');
				$("img[job-id]").hide();
				$("button[job-id]").show();
				alert('Desculpe-nos, fizemos alguma coisa errada: ' + error);
			}
		});
	});

	// toggle visibility after content is loaded...
	$(document).on("click", ".job-wrapper-details button.show-details" , function() {
		_this = $(this).parent('.job-wrapper-details');
		details = _this.children("div.job-details");
		button = $(this);
		details.toggle({
			duration: 'fast',
			complete: function(){
				_this.toggleClass('wrapper-expanded wrapper-contracted');
				button.text(details.is(":visible") ? "- detalhes" : "+ detalhes");
			}
		});
	});

	$(document).on("click", ".job a" , function(e) {
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
		job_titles = [];
		_locations = [];
		$(".jobtitle-item:checked").each(function(){
			job_titles.push($(this).val());
		});
		$(".city-item:checked").each(function(){
			_locations.push($(this).val());
		});
		data = {
			term: q,
			job_titles: job_titles.join("-"),
			cities: _locations.join("-"),
			days: $("#period-days").val(),
			page: page,
			csrfmiddlewaretoken: '{{ csrf_token }}'
		};
		$("#search-loading-img").show();
		$("#search-search-info").hide();
		search("/vagas/parcial/buscar/", 'post', data, callback);
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
});