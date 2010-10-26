var comments = document.getElementById('comments');
if (comments && !comments.getAttribute('class')) {
	comments.setAttribute('class', 'denoizer');

	// Добавляем стили, чтобы меньше всего делать скриптами.
	var css = document.createElement('style');
	css.type = 'text/css';
	css.appendChild(document.createTextNode(
		'.denoizer .denoize > .msg-meta, .denoizer .denoize > .entry-content, .denoizer .comment_holder > .ufo-was-here { display: none; }' +
		'.denoizer .denoize > ul.entry { margin-left: 0; }' +
		'.denoizer .ndnzr { display: block; } .ndnzr { display: none; }'));
	document.getElementsByTagName('head')[0].appendChild(css);

	// Находим все блоки с суммой голосов.
	var count = 0, marks = document.querySelectorAll('.vote');
	if (marks) {
		for (idx = 0; idx < marks.length; idx++) {
			if (marks[idx].getAttribute('class').indexOf(' positive') == -1) {
				var c = marks[idx].parentNode.parentNode.parentNode.parentNode;
				c.setAttribute('class', c.getAttribute('class') + ' denoize');
				count++;
			}
		}
	}

	if (count) {
		var l = document.createElement('div');
		l.innerHTML = '<a class="ndnzr" href="#comments" onClick="document.getElementById(&quot;comments&quot;).setAttribute(&quot;class&quot;, &quot;&quot;)">Показать скрытые комментарии</a>';
		document.getElementById('comments').appendChild(l);
	}
}

// vim: set ts=4 sts=4 sw=4 noet:
