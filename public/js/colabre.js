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
});