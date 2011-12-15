// ==UserScript==
// @include http://friendfeed.com/*
// ==/UserScript==
//
// Replaces custom user names with the real ones.

(function () {
	window.addEventListener("load", function () {
		var tags = document.getElementsByClassName("l_profile");

		for (idx in tags) {
			var tag = tags[idx];
			tag.innerHTML = tag.getAttribute("href").substring(1);
		}
	}, false);
})();
