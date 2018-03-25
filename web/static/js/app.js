document.addEventListener("DOMContentLoaded", function (event) {
    var vote = document.getElementsByClassName("vote");
    console.warn(vote);
    Array.prototype.forEach.call(vote, function (elvote) {
        var id = elvote.dataset.id;
        Array.prototype.forEach.call(elvote.querySelectorAll("a"), function (el) {
            el.addEventListener("click", function (event) {
                var type = el.classList[0];
                console.info(id, type);
                var request = new XMLHttpRequest();
                request.open("POST", "/api/vote/" + id + "/" + type, true);

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

});
