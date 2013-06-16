var search = function(url, type, data, success_callback, error_callback, complete_callback, beforeSend_callback)
{
	$.ajax({
		url: url,
		type: type,
		data: data,
		success: function(result)
		{
			success_callback(result);
		},
		error: function(a, b, error)
		{
			if(typeof(error_callback) == "function")
			{
				error_callback(error);
			}
		},
		complete: function()
		{
			if(typeof(complete_callback) == "function")
			{
				complete_callback();
			}
		},
		beforeSend: function()
		{
			if(typeof(beforeSend_callback) == "function")
			{
				beforeSend_callback();
			}
		}
	});
};