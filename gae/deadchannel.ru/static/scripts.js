$(document).ready(function(){
	$('.sform .check').change(check_boxes);
	$('.sform .text').keyup(check_sbutton);

	// На случай если форма загружена с отмеченными чекбоксами.
	check_boxes();

	// Передаём фокус первому полю формы, если есть.
	$('form input:first').focus();
});

function check_boxes()
{
	var div_sel = '#' + $(this).attr('name') + '_div';
	$(div_sel).toggleClass('hidden');
	$(div_sel + ' .text').attr('value', '');
	$(div_sel + ' .text').focus();
	check_sbutton();
}

function check_sbutton()
{
	var text = $('#phone_div .text').attr('value')
		+ $('#email_div .text').attr('value');
	$('.sform .button input').attr('disabled', text.length ? '' : 'disabled');
}
