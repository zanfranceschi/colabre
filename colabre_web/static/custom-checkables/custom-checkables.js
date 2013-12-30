$(function() {

	$("input[type=checkbox]").each(function(){
		fakeCb = $("<a class='checkable checkable-checkbox' cc-data-target='#" + $(this).prop("id") + "'></a>");
		fakeCb.addClass($(this).prop("class"));
		$(this).after(fakeCb);
	});
	
	$("input[type=radio]").each(function() {
		fakeRd = $("<a class='checkable checkable-radio' cc-data-target='#" + $(this).prop("id") + "' cc-data-target-value='" + $(this).val() + "' cc-data-target-name='" + $(this).prop("name") + "'></a>");
		fakeRd.addClass($(this).prop("class"));
		$(this).after(fakeRd);
	});
	
	$("input[type=radio], input[type=checkbox]").hide();
	
	$(document).on("click", "a.checkable-checkbox, a.checkable-radio", function() {
		eleId = $(this).attr("cc-data-target");
		$(eleId).trigger("click");
	});
	
	$(document).on("change", ":checkbox", function(){
		ele = $("a[cc-data-target='#" + $(this).prop("id") + "']");
		if($(this).prop("checked"))
		{
			ele.addClass("checkable-checkbox-checked");
		}
		else
		{
			ele.removeClass("checkable-checkbox-checked");
		}
	});
	
	$(":radio").change(function(){
		console.log($(this).prop("checked"));
		$("a[cc-data-target-name='" + $(this).prop("name") + "']").removeClass("checkable-radio-checked"); // unselect all
		$("a[cc-data-target-name='" + $(this).prop("name") + "'][cc-data-target-value='" + $(this).val() + "']").addClass("checkable-radio-checked"); // select one actually selected
	});
	
	
	$("input[type=checkbox]:checked").each(function(){
		$("a[cc-data-target=#" + $(this).prop("id") + "]").addClass("checkable-checkbox-checked");
	});
	
	$("input[type=radio]:checked").each(function(){
		$("a[cc-data-target-name='" + $(this).prop("name") + "'][cc-data-target-value='" + $(this).val() + "']").addClass("checkable-radio-checked");
	});
	
});
