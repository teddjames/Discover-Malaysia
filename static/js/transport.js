document.addEventListener("DOMContentLoaded", function () {

    const compareButton =
        document.getElementById("compareTransport");

    const fromSelect =
        document.getElementById("transportFrom");

    const toSelect =
        document.getElementById("transportTo");

    const resultsContainer =
        document.querySelector(".transport-results");


    compareButton.addEventListener("click", async function () {

        const origin = fromSelect.value;

        const destination = toSelect.value;


        if (origin === destination) {

            alert("Please choose two different locations.");

            return;
        }


        compareButton.textContent = "Comparing...";

        compareButton.disabled = true;


        try {

            const response = await fetch(
                `/api/transport?origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}`
            );


            const data = await response.json();


            if (!response.ok) {

                throw new Error(
                    data.error || "Unable to retrieve transport information."
                );

            }


            displayTransportResults(data);


        } catch (error) {

            console.error(error);

            resultsContainer.innerHTML = `
                <p class="transport-error">
                    Unable to find transport information for this route.
                </p>
            `;

        } finally {

            compareButton.textContent = "Compare";

            compareButton.disabled = false;

        }

    });


    function displayTransportResults(data) {

        if (!data.routes || data.routes.length === 0) {

            resultsContainer.innerHTML = `

                <div class="no-transport">

                    <h3>
                        No transport routes found
                    </h3>

                    <p>
                        We don't currently have transport
                        information for this route.
                    </p>

                </div>

            `;

            return;
        }


        let html = `

            <div class="transport-results-header">

                <div>

                    <span class="section-label">
                        ROUTE OPTIONS
                    </span>

                    <h3>
                        ${data.origin}
                        →
                        ${data.destination}
                    </h3>

                </div>

                <span>
                    ${data.routes.length} options
                </span>

            </div>

        `;


        data.routes.forEach(function (route) {

            const icon =
                getTransportIcon(route.transport_type);


            const duration =
                formatDuration(route.duration_minutes);


            const price =
                formatPrice(
                    route.min_price,
                    route.max_price
                );


            html += `

                <div class="transport-card">

                    <div class="transport-icon">
                        ${icon}
                    </div>


                    <div class="transport-info">

                        <span>
                            ${route.transport_type.toUpperCase()}
                        </span>

                        <h4>
                            ${route.transport_type}
                        </h4>

                        <p>
                            ${route.notes || ""}
                        </p>

                    </div>


                    <div class="transport-details">

                        <strong>
                            ${duration}
                        </strong>

                        <span>
                            Estimated journey
                        </span>

                    </div>


                    <div class="transport-price">

                        <strong>
                            ${price}
                        </strong>

                        <span>
                            Estimated
                        </span>

                    </div>

                </div>

            `;

        });


        resultsContainer.innerHTML = html;

    }


    function getTransportIcon(type) {

        const transportType =
            type.toLowerCase();


        if (transportType === "train") {
            return "🚆";
        }


        if (transportType === "bus") {
            return "🚌";
        }


        if (transportType === "grab") {
            return "🚗";
        }


        return "🚍";

    }


    function formatDuration(minutes) {

        if (minutes < 60) {

            return `${minutes} min`;

        }


        const hours =
            Math.floor(minutes / 60);

        const remainingMinutes =
            minutes % 60;


        if (remainingMinutes === 0) {

            return `${hours} hr`;

        }


        return `${hours} hr ${remainingMinutes} min`;

    }


    function formatPrice(min, max) {

        if (min === max) {

            return `RM ${min}`;

        }


        return `RM ${min}–${max}`;

    }

});