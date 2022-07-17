function build_simple_date_string(date) {
    let date_string = date.getFullYear() + "-";
    if (date.getMonth() + 1 < 10) {
        date_string += '0';
    }
    date_string += (date.getMonth() + 1) + "-";
    if (date.getDate() < 10) {
        date_string += '0';
    }
    date_string += date.getDate();
    return date_string;
}

class GitActivityWidget extends SlugWidget {
    constructor(element, options) {
        super(element, options);
        this.commits = [];
        this.commit_block_elements = {};
        this.element_table = this.build_table(52 * 7);
        this.element_wrapper = crel('div',
            { "class": "table-wrapper"},
            this.element_table
        );
        // Title isn't used ATM
        //this.element_title = crel('div',
        //    { "class": "title" },
        //    "Activity over the previous 52 weeks"
        //);
        //this.element.appendChild(this.element_title);
        this.element.appendChild(crel('div', this.element_wrapper));

        let now = new Date();
        let today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        let then_stamp = ((today.getTime() - (1000 * 60 * 60 * 24 * 52 * 7)) / 1000);

        let url = "/api/git/commits" +
            "?project=" + options.project +
            "&datefrom=" + then_stamp;

        api_call(url,
            function(response) {
                let year = (new Date()).getFullYear();
                if (response.length == 0) {
                    this.new_year_table(year);
                }
                this.update_commits(response);
            }.bind(this),
            function(response) {
                console.log(response);
            }
        );

    }

    build_table(day_count) {
        /* Create the dom table */
        let year_table = crel('table', { class: "year-table" });
        let now = new Date();
        let today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        let day_one = new Date(today.getTime() - (1000 * 60 * 60 * 24 * day_count));
        let day_offset = (today).getDay();

        let months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        let weekdays = ['Sun', 'Mon', 'Tue', 'Wed', "Thu", 'Fri', 'Sat'];
        // Create a new row for the weekday labels,
        // The first column is a usually empty column that may contain a month label
        year_table.appendChild(crel('tr', crel('th')));
        for (let i = 0; i < 7; i++) {
            year_table.lastChild.appendChild(crel('th', weekdays[i % 7]));
        }

        year_table.appendChild(crel('tr'));

        // Add padding on the right-hand side of the table
        // None is needed for Saturday
        if (day_offset != 6) {
            for (let i = 0; i < 7 - day_offset; i++) {
                year_table.lastChild.appendChild(crel('td', { 'class': 'oob' }, crel('div')));
            }
        }

        let day_one_ts = day_one.getTime();
        let previous_month = today.getMonth();
        let month_changed = true;
        let month_changed_last_row = false;

        let previous_year = today.getFullYear();
        let year_changed = false;

        for (let i = day_count; i >= 0; i--) {
            let timestamp = day_one_ts + (i * (24 * 60 * 60 * 1000));
            let working_date = new Date(timestamp);
            let date_string = build_simple_date_string(working_date);
            let doy = working_date.getTime() - (new Date(working_date.getFullYear(), 0, 0));
            doy = parseInt(doy / (1000 * 60 * 60 * 24));


            let td = crel('td',
                {
                    'data-date': date_string,
                    'class': (working_date.getMonth() % 2 == 0 ? "evenmonth" : "")
                },
                crel('div')
            );
            this.commit_block_elements[(working_date.getFullYear() * 366) + doy] = td;

            // If this is the first pass through the loop AND a new row is requested,
            // That means day_offset is saturday and we don't need a new row yet
            if (i < day_count) {
                if ((i + day_offset) % 7 == 6) {
                    // If the month changed, add the month label to the buffer column cell
                    if (month_changed) {
                        let buffer = crel('td',
                            {
                                'rowspan': 2,
                                "class": "month-label"
                            },
                            months[working_date.getMonth()]
                        );
                        month_changed = false;
                        month_changed_last_row = true;
                        year_table.lastChild.insertBefore(buffer, year_table.lastChild.firstChild);
                    } else if (month_changed_last_row) {
                        // Don't add a buffer cell
                        month_changed_last_row = false;
                    } else {
                        let buffer = crel('td');
                        year_table.lastChild.insertBefore(buffer, year_table.lastChild.firstChild);
                    }

                    // Add an entire new row to delimit a new year
                    if (year_changed) {
                        let divider = crel('tr',
                            crel('td'),
                            crel('td',
                                {
                                    'colspan': 7,
                                    'class': 'year-delim'
                                },
                                crel('span',
                                    crel('hr'),
                                    crel('div', previous_year),
                                    crel('hr')
                                )
                            )
                        );
                        year_table.insertBefore(divider, year_table.lastChild);
                        year_changed = false;
                    }
                    year_table.appendChild(crel('tr'));
                }
            }
            year_changed |= previous_year != working_date.getFullYear();
            previous_year = working_date.getFullYear();
            month_changed |= previous_month != working_date.getMonth();
            previous_month = working_date.getMonth();

            year_table.lastChild.insertBefore(td,year_table.lastChild.firstChild);
        }

        if (!month_changed_last_row && year_table.lastChild.childNodes.length != 0) {
            year_table.lastChild.insertBefore(crel('td'), year_table.lastChild.firstChild);
        }

        return year_table;
    }


    update_commits(new_commits) {
        /* Add a list of new commits to the widget. Update the table cells accordingly */
        for (let i = 0; i < new_commits.length; i++) {
            let commit = new_commits[i];
            let date = new Date(commit.date * 1000);
            let working_year = date.getFullYear();

            let day_one = new Date(working_year, 0, 1);
            let one_day = 1000 * 60 * 60 * 24
            let doy = (date.getTime() - day_one.getTime()) / one_day;
            let key = Math.floor((366 * working_year) + doy);

            let element_td = this.commit_block_elements[key];

            let commit_count = element_td.getAttribute('data-count');
            if (!commit_count) {
                commit_count = 0;
            }

            commit_count = parseInt(commit_count) + 1;
            element_td.setAttribute('data-count', commit_count);
            element_td.setAttribute('title', commit_count + " commits on " + element_td.getAttribute('data-date'));
            element_td.classList.add('active');

            this.commits.push[commit];
        }
    }
}


class CloneButtonWidget extends SlugWidget {
    constructor(element, options) {
        super(element, options);
        this.url = 'git://' + location.hostname + '/' + options.project;
        this.element_clone = crel('div', 'Clone URL');
        this.element_url = crel('div', { 'tabindex': 0 }, this.url);
        this.element.appendChild(
            crel('div',
                this.element_clone,
                this.element_url
            )
        );

        event_listen(this.element_clone, 'click', function() {
            navigator.clipboard.writeText(this.element_url.innerText)
            .then(() => {
                let offset_width = this.element_clone.offsetWidth;
                this.element_clone.innerText = "Copied";
                this.element_clone.classList.add("copied");
                setTimeout(function() {
                    this.element_clone.innerText = "Clone URL";
                    this.element_clone.classList.remove("copied");
                }.bind(this), 1000);
            })
            .catch(err => {
                alert('Error in copying text: ', err);
            });
        }.bind(this));
    }
}

class GitBranchSelect extends SlugWidget {
    constructor(element, options) {
        super(element, options);
        this.project_name = options.project;

        let option_nodes = [];
        for (let i = 0; i < options.branches.length; i++) {
            let option = crel('option',
                { value: options.branches[i] },
                options.branches[i]
            );
            option_nodes.push(option);
        }

        this.select = new CustomSelect(option_nodes, function(new_value) {
            let new_location = "/project/" + encodeURIComponent(this.project_name);
            new_location += "?branch=" + encodeURIComponent(new_value);
            location.href = new_location;
        }.bind(this));

        this.select.set(options.active);

        this.element.appendChild(this.select.element);
    }
}

class GitCommitSelect extends SlugWidget {
    constructor(element, options) {
        super(element, options);
        this.project_name = options.project;
        this.branch_name = options.branch;
        this.project_path = options.path;

        let option_nodes = [];
        for (let i = 0; i < options.commits.length; i++) {
            let commit = options.commits[i];
            let date = new Date(commit.date * 1000);
            let label_string = build_simple_date_string(date);
            label_string = commit.id.substr(0,8) + " - " + label_string;

            option_nodes.push(
                crel('option',
                    { value: commit.id },
                    label_string
                )
            );
        }

        this.select = new CustomSelect(option_nodes, function(new_value) {
            let new_location = "/project/" + encodeURIComponent(this.project_name);
            new_location += "?branch=" + encodeURIComponent(this.branch_name);
            new_location += "&commit=" + encodeURIComponent(new_value);
            location.href = new_location;
        }.bind(this));

        if (options.active) {
            this.select.set(options.active);
        } else {
            this.select.set(options.commits[0].id);
        }


        this.element.appendChild(this.select.element);
    }
}

