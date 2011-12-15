// ==UserScript==
// @include http://news2.ru/story/*
// ==/UserScript==
//
// Pins the vote box to the top of news2.ru story pages, so that you wouldn't
// forget to vote after reading the comments.
//
// code.umonkey.net

(function () {
	var init_css = true;

	function on_scroll() {
		if (init_css) {
			css = document.createElement("style");
			css.type = "text/css";
			css.innerHTML = ".vote_placeholder.pinned { position: fixed; top: 10px; z-index: 100; } .news_body { margin-left: 60px }";
			document.body.appendChild(css);
			init_css = false;
		}

		try {
			var div = document.getElementsByClassName("vote_placeholder");
			if (!div.length)
				return;  // layout changed

			var desc = document.getElementsByClassName("news_description");
			if (!desc.length)
				return;  // layout changed
			var limit = desc[0].offsetTop;

			var y = document.documentElement.scrollTop;

			if (y > limit - 10) {
				div[0].className = "vote_placeholder pinned";
			} else {
				div[0].className = "vote_placeholder";
			}
		} catch (e) {
			alert(e);
		}
	}

	window.addEventListener("scroll", on_scroll, false);
})();
