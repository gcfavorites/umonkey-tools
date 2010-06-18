// Habrahabr Denoiser v1.8
// justin.forest@gmail.com, 2010. Public Domain.
// http://code.google.com/p/umonkey-tools/wiki/habranoise

// ==Userscript==
// @name Habrahabr Denoiser
// @author justin.forest@gmail.com
// @namespace http://umonkey.net/
// @version 1.8
// @description Hides comments that were modded down.
// @include http://habrahabr.ru/blogs/*
// @include http://*.habrahabr.ru/blogs/*
// ==/Userscript==

window.addEventListener('DOMContentLoaded', function(){
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
		var count = find_cb('ul', 'vote', function (div) {
			if (div.getAttribute('class').indexOf(' positive') == -1) {
				var c = div.parentNode.parentNode.parentNode.parentNode;
				c.setAttribute('class', c.getAttribute('class') + ' denoize');
				return 1;
			}
			return 0;
		});
		if (count) {
			var l = document.createElement('div');
			l.innerHTML = '<a class="ndnzr" href="#comments" onClick="document.getElementById(&quot;comments&quot;).setAttribute(&quot;class&quot;, &quot;&quot;)">Показать скрытые комментарии</a>';
			document.getElementById('comments').appendChild(l);
		}
	}
}, false);

function find_cb(t, c, f)
{
	var count = 0;
	if (document.querySelectorAll) {
		var idx, marks = document.querySelectorAll(t + '.' + c);
		if (marks)
			for (idx = 0; idx < marks.length; idx++)
				count += f(marks[idx]);
	} else {
		var cls, idx, marks = document.getElementsByTagName(t);
		if (marks) {
			for (idx = 0; idx < marks.length; idx++) {
				cls = marks[idx].getAttribute('class');
				if (cls && cls.substring(0, c.length) == c)
					count += f(marks[idx]);
			}
		}
	}
	return count;
}

// vim: set ts=4 sts=4 sw=4 noet:
