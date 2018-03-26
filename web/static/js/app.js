document.addEventListener("DOMContentLoaded", function (event) {
    var vote = document.getElementsByClassName("vote");
    console.warn(vote);
    Array.prototype.forEach.call(vote, function (elvote) {
        var id = elvote.dataset.id;
        var type = elvote.dataset.type;
        Array.prototype.forEach.call(elvote.querySelectorAll("a"), function (el) {
            el.addEventListener("click", function (event) {
                console.info(elvote);
                var vote = el.classList[0];
                console.info(type, id, vote);
                var request = new XMLHttpRequest();
                request.open("POST", "/api/vote/" + type + "/" + id + "/" + vote, true);

                request.onload = function () {
                    if (this.status >= 200 && this.status < 400) {
                        var resp = JSON.parse(this.response);
                        console.info(resp);
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
                list: list
            });
            input.addEventListener("awesomplete-select", function (event) {
                if (!(event.text.value in resp)) { // shouldn't happen
                    return false
                }
                var selectedSite=resp[event.text.value];
                window.location.href="/s/"+selectedSite.url
                
            });
        } else {
            // We reached our target server, but it returned an error

        }
    };
    request.onerror = function () {
        // There was a connection error of some sort
    };
    request.send();

});
