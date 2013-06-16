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

$(function(){
	$(".message-close-btn").click(function(){
		$(this).parent().fadeOut(200);
	});

	$(".message").click(function(){
		$(this).fadeOut(200);
	});


	$("[title]").not('input, textarea, .custom-tooltip').tooltip({

	      // a little tweaking of the position
	      offset: [-2, 10],

	      // use the built-in fadeIn/fadeOut effect
	      effect: "fade",

	      // custom opacity setting
	      opacity: 0.7

	}).dynamic({ bottom: { direction: 'down', bounce: true } });


	$("input[title], textarea[title]").tooltip({

		// place tooltip on the right edge
		position: 'center right',

		// a little tweaking of the position
		offset: [-2, 10],

		// use the built-in fadeIn/fadeOut effect
		effect: "fade",

		// custom opacity setting
		opacity: 0.7

	});

	$.tools.dateinput.localize("pt-br",  {
		months:
			'Janeiro,Fevereiro,Março,Abril,Maio,Junho,Julho,Agosto,Setembro,Outubro,Novembro,Dezembro',
	shortMonths:
			'jan,fev,mar,abr,mai,jun,jul,ago,set,out,nov,dez',
	days:          'domingo,segunda-feira,terça-feira,quarta-feira,quinta-feira,sexta-feira,sábado',
	shortDays:     'dom,seg,ter,qua,qui,sex,sáb'
	});
	/*
	$(".date-input").dateinput({
		format: 'dd/mm/yyyy',
		lang: 'pt-br'
	});
	*/
});



