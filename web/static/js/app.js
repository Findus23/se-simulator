document.addEventListener("DOMContentLoaded", function (event) {
    var vote = document.getElementsByClassName("vote");
    Array.prototype.forEach.call(vote, function (elvote) {
        var id = elvote.dataset.id;
        var type = elvote.dataset.type;
        Array.prototype.forEach.call(elvote.querySelectorAll("a"), function (el) {
            el.addEventListener("click", function (event) {
                var vote = el.classList[0];
                var request = new XMLHttpRequest();
                request.open("POST", "/api/vote/" + type + "/" + id + "/" + vote, true);

                request.onload = function () {
                    if (this.status >= 200 && this.status < 400) {
                        var resp = JSON.parse(this.response);
                        el.classList.add("active");
                        elvote.querySelector("div").textContent = resp.upvotes - resp.downvotes
                    } else {
                        // We reached our target server, but it returned an error

                    }
                };
                request.onerror = function () {
                    // There was a connection error of some sort
                };
                request.send();
            })
        });
    });
    var input = document.getElementById("siteselector");
    var check = document.getElementById("check");
    var header = document.getElementsByClassName("siteheader")[0];
    var retry = document.getElementById("retry");
    var selectedSite, headerimg, headertitle, entered;

    function toast(type, message) {
        console.warn(type, message)
    }

    function checkQuiz(selection, id) {
        console.info(selection, id);
        input.disabled = true;
        check.disabled = true;
        var request = new XMLHttpRequest();
        request.open("POST", "/api/quiz/" + id + "/" + selection.url, true);

        request.onload = function () {
            if (this.status >= 200 && this.status < 400) {
                var resp = JSON.parse(this.response);
                console.log(resp.correct);
                headertitle.innerText = resp.site.name;
                headerimg.src = resp.site.icon_url;
                header.style.backgroundColor = resp.site.tag_background_color;
                header.style.color = resp.site.link_color;
                var result = document.getElementById(resp.correct ? "correct" : "incorrect");
                result.style.display = "block";
                retry.focus()
            } else {
                // We reached our target server, but it returned an error

            }
        };
        request.onerror = function () {
            // There was a connection error of some sort
        };
        request.send();

    }

    if (input) {
        var mode = input.dataset.mode;
        var request = new XMLHttpRequest();
        request.open("GET", "/api/sites", true);

        request.onload = function () {
            if (this.status >= 200 && this.status < 400) {
                var resp = JSON.parse(this.response);
                var list = [];
                for (var key in resp) {
                    if (resp.hasOwnProperty(key)) {
                        var site, shortname;
                        site = resp[key];
                        shortname = site.url.replace(".stackexchange.com", ".SE");
                        list.push({
                            label: site.name + " (" + shortname + ")",
                            value: site.url
                        });
                    }
                }
                new Awesomplete(input, {
                    list: list,
                    minChars: 0,
                    autoFirst: true
                });
                if (mode === "quiz") {
                    console.log(input);
                    input.focus()
                }
                input.addEventListener("awesomplete-select", function (event) {
                    if (!(event.text.value in resp)) { // shouldn't happen
                        return false
                    }
                    selectedSite = resp[event.text.value];

                    if (mode === "filter") {
                        window.location.href = "/s/" + selectedSite.url
                    } else if (mode === "quiz") {
                        input.focus();

                        entered = true;
                        console.log(selectedSite);
                        check.style.backgroundColor = selectedSite.tag_background_color;
                        header.style.backgroundColor = selectedSite.tag_background_color;
                        check.style.color = selectedSite.link_color;
                        header.style.color = selectedSite.link_color;
                        while (header.firstChild) {
                            header.removeChild(header.firstChild);
                        }
                        headerimg = new Image(30, 30);
                        headerimg.src = selectedSite.icon_url;
                        headertitle = document.createElement('span');
                        headertitle.innerText = selectedSite.name + "?";
                        header.appendChild(headerimg);
                        header.appendChild(headertitle);
                    }
                });
            } else {
                // We reached our target server, but it returned an error

            }
        };
        request.onerror = function () {
            // There was a connection error of some sort
        };
        request.send();
        if (mode === "quiz") {
            var handler = function (event) {
                // event.preventDefault();
                if (event.keyCode === 13 && entered) {
                    checkQuiz(selectedSite, input.dataset.id);
                    input.removeEventListener("keydown", handler, false)
                }
            };
            input.addEventListener("keydown", handler);
            input.addEventListener("input", function () {
                entered = false
            });
            check.addEventListener("click", function () {
                if (entered) {
                    checkQuiz(selectedSite, input.dataset.id);

                } else {
                    toast("warning", "please select a site")
                }
            });
            retry.addEventListener("click", function () {
                window.location.reload(true);
            });
            retry.addEventListener("click", function (event) {
                if (event.keyCode === 13) {
                    window.location.reload(true);
                }
            });

        }

    }

});
