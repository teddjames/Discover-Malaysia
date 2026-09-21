document.addEventListener(
    "DOMContentLoaded",
    function () {


        const plannerOptions =
            document.querySelectorAll(
                ".planner-option"
            );


        const generateTrip =
            document.getElementById(
                "generateTrip"
            );


        const itineraryResults =
            document.getElementById(
                "itineraryResults"
            );


        // ==========================================
        // OPTION SELECTION
        // ==========================================

        plannerOptions.forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        const type =
                            button.dataset.type;


                        // Single-selection options

                        if (
                            type === "days" ||
                            type === "budget"
                        ) {

                            document
                                .querySelectorAll(
                                    `.planner-option[data-type="${type}"]`
                                )
                                .forEach(
                                    function (option) {

                                        option.classList
                                            .remove(
                                                "selected"
                                            );

                                    }
                                );


                            button.classList.add(
                                "selected"
                            );

                        }


                        // Multiple-selection options

                        else {

                            button.classList.toggle(
                                "selected"
                            );

                        }

                    }
                );

            }
        );


        // ==========================================
        // BUILD TRIP
        // ==========================================

        generateTrip.addEventListener(
            "click",
            async function () {


                const daysButton =
                    document.querySelector(
                        '.planner-option[data-type="days"].selected'
                    );


                const budgetButton =
                    document.querySelector(
                        '.planner-option[data-type="budget"].selected'
                    );


                const interestButtons =
                    document.querySelectorAll(
                        '.planner-option[data-type="interest"].selected'
                    );


                const destinationButtons =
                    document.querySelectorAll(
                        '.planner-option[data-type="destination"].selected'
                    );


                // ----------------------------------
                // GET VALUES
                // ----------------------------------

                const days =
                    daysButton
                        ? Number(
                            daysButton.dataset.value
                        )
                        : null;


                const budget =
                    budgetButton
                        ? budgetButton.dataset.value
                        : null;


                const interests =
                    Array.from(
                        interestButtons
                    ).map(
                        button =>
                            button.dataset.value
                    );


                const destinations =
                    Array.from(
                        destinationButtons
                    ).map(
                        button =>
                            button.dataset.value
                    );


                // ----------------------------------
                // VALIDATION
                // ----------------------------------

                if (!days || !budget) {

                    alert(
                        "Please select your trip length and budget."
                    );

                    return;

                }


                if (
                    destinations.length === 0
                ) {

                    alert(
                        "Please select at least one destination."
                    );

                    return;

                }


                // ----------------------------------
                // LOADING
                // ----------------------------------

                generateTrip.disabled =
                    true;


                generateTrip.textContent =
                    "Building Your Trip...";


                itineraryResults.innerHTML = `

                    <div class="planner-loading">

                        <span class="section-label">
                            YOUR ITINERARY
                        </span>

                        <h2>
                            Building your trip...
                        </h2>

                        <p>
                            Finding the best activities
                            for your trip.
                        </p>

                    </div>

                `;


                try {


                    // ----------------------------------
                    // SEND REQUEST
                    // ----------------------------------

                    const response =
                        await fetch(
                            "/api/trip-planner",
                            {

                                method:
                                    "POST",

                                headers: {

                                    "Content-Type":
                                        "application/json"

                                },

                                body:
                                    JSON.stringify({

                                        days:
                                            days,

                                        budget:
                                            budget,

                                        interests:
                                            interests,

                                        destinations:
                                            destinations

                                    })

                            }
                        );


                    const data =
                        await response.json();


                    if (!response.ok) {

                        throw new Error(
                            data.error ||
                            "Unable to build itinerary."
                        );

                    }


                    // ----------------------------------
                    // DISPLAY
                    // ----------------------------------

                    displayItinerary(
                        data
                    );


                } catch (error) {

                    console.error(
                        error
                    );


                    itineraryResults.innerHTML = `

                        <div class="planner-error">

                            <span class="section-label">
                                ERROR
                            </span>

                            <h2>
                                We couldn't build your trip.
                            </h2>

                            <p>
                                ${error.message}
                            </p>

                        </div>

                    `;

                }


                generateTrip.disabled =
                    false;


                generateTrip.textContent =
                    "Build My Trip →";

            }
        );


        // ==========================================
        // DISPLAY ITINERARY
        // ==========================================

        function displayItinerary(
            data
        ) {


            if (
                !data.itinerary ||
                data.itinerary.length === 0
            ) {

                itineraryResults.innerHTML = `

                    <div class="planner-empty">

                        <span class="section-label">
                            NO MATCHES
                        </span>

                        <h2>
                            We couldn't build your itinerary.
                        </h2>

                        <p>
                            Try selecting different
                            destinations or interests.
                        </p>

                    </div>

                `;

                return;

            }


            // ----------------------------------
            // HEADER
            // ----------------------------------

            let html = `

                <div class="itinerary-header">

                    <span class="section-label">
                        YOUR PERSONAL ITINERARY
                    </span>

                    <h2>
                        Your ${data.days}-day
                        Malaysia experience
                    </h2>

                    <p>
                        A personalised itinerary
                        based on your destinations,
                        interests and budget.
                    </p>

                </div>


                <div class="itinerary-days">

            `;


            // ----------------------------------
            // EACH DAY
            // ----------------------------------

            data.itinerary.forEach(
                function (day) {


                    html += `

                        <section
                            class="itinerary-day"
                        >

                            <div
                                class="itinerary-day-header"
                            >

                                <span>
                                    DAY ${day.day}
                                </span>

                                <h3>
                                    ${getDayTitle(
                                        day,
                                        data
                                    )}
                                </h3>

                            </div>


                            <div
                                class="day-activities"
                            >

                    `;


                    // ----------------------------------
                    // ACTIVITIES
                    // ----------------------------------

                    if (
                        day.activities.length === 0
                    ) {

                        html += `

                            <p>
                                No activities
                                available for
                                this day.
                            </p>

                        `;

                    }


                    day.activities.forEach(
                        function (activity, index) {


                            const time =
                                getActivityTime(
                                    index
                                );


                            html += `

                                <article
                                    class="itinerary-activity"
                                >

                                    <div
                                        class="activity-time"
                                    >

                                        ${time}

                                    </div>


                                    <div
                                        class="activity-content"
                                    >

                                        <span
                                            class="activity-category"
                                        >
                                            ${activity.category}
                                        </span>


                                        <h4>
                                            ${activity.name}
                                        </h4>


                                        <p>
                                            ${activity.description}
                                        </p>


                                        <div
                                            class="activity-meta"
                                        >

                                            <span>
                                                📍
                                                ${activity.destination}
                                            </span>

                                            <span>
                                                ⏱
                                                ${activity.duration}
                                            </span>

                                            <span>
                                                ⭐
                                                ${activity.rating}
                                            </span>

                                            <span>
                                                RM
                                                ${activity.price}
                                            </span>

                                        </div>

                                    </div>

                                </article>

                            `;

                        }
                    );


                    // ----------------------------------
                    // DAY SUMMARY
                    // ----------------------------------

                    html += `

                            </div>


                            <div
                                class="day-summary"
                            >

                                <span>
                                    💰 Estimated activities:
                                    RM ${day.total_cost}
                                </span>

                                <span>
                                    📍
                                    ${day.destinations.join(
                                        " • "
                                    )}
                                </span>

                            </div>

                        </section>

                    `;

                }
            );


            html += `

                </div>

            `;


            itineraryResults.innerHTML =
                html;


            // Scroll to results

            itineraryResults.scrollIntoView({
                behavior: "smooth"
            });

        }


        // ==========================================
        // DAY TITLE
        // ==========================================

        function getDayTitle(
            day,
            data
        ) {

            if (
                day.destinations &&
                day.destinations.length > 0
            ) {

                return day.destinations.join(
                    " + "
                );

            }


            return data.destinations[0];

        }


        // ==========================================
        // ACTIVITY TIMES
        // ==========================================

        function getActivityTime(
            index
        ) {

            const times = [

                "09:00 AM",

                "12:00 PM",

                "03:00 PM",

                "07:00 PM"

            ];


            return times[index]
                || "Later";

        }

    }
);