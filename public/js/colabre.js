$(function(){
	var ajaxRequest;
	
	$("html").ajaxSend(function(event, jqXHR, ajaxOptions){
		ajaxRequest = jqXHR;
	});
	
	$("html").ajaxError(function(event, jqXHR, ajaxOptions, exception){
		$(".disable-in-request").removeAttr("disabled");
		if(exception != "abort")
		{
			alert(exception);
		}
	});
	
	$("#ajax-request-cancel").click(function(){
		if (ajaxRequest)
			ajaxRequest.abort();
			$(".disable-in-request").removeAttr("disabled");
	});
	
	$("#ajax-request").bind("ajaxSend", function(){
		$(this).show();
		
	}).bind("ajaxComplete", function(){
		$(this).hide();
		$(".disable-in-request").removeAttr("disabled");
	});
	
	$('.search-onclick').keydown(function (e){
		if(e.keyCode == 13)
		{
			search();
		}
	});
	
	$('input[label]').css({"color" : "#ccc"});
	
	$('input[label]').each(function(){
		$(this).val($(this).attr("label"));
	});
	
	$('input[label]').blur(function(){
		
		label = $(this).attr("label");
		
		if ($(this).val().length == 0)
		{
			$(this).val(label);
			$(this).css({"color" : "#ccc"});
		}
	});
	
	$('input[label]').focus(function(){
		
		label = $(this).attr("label");
		
		if ($(this).val().length == 0 || $(this).val() == label)
		{
			$(this).val('');
			$(this).css({"color" : "#000"});
		}
	});
});