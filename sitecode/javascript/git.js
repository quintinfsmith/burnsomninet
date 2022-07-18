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
    MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    WEEKDAYS = ['S', 'M', 'T', 'W', "T", 'F', 'S'];
    WEEKDAY_OFFSET = 1; // Start at monday
    constructor(element, options) {
        super(element, options);
        this.commits = [];
        this.commit_block_elements = {};

        let day_one;
        if (options.datefrom) {
            day_one = new Date(options.datefrom);
            day_one = new Date(day_one.getFullYear(), day_one.getMonth(), day_one.getDate());
        } else {
            let now = new Date();
            day_one = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
        }

        let first_date;
        if (options.datefirst) {
            first_date = new Date(options.datefirst);
        } else {
            first_date = null;
        }

        this.element_table = this.build_vertical_table(day_one, first_date);
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

        if (options.commits.length) {
            this.update_commits(options.commits);
        } else {
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

    }

    build_row_data(from_date, first_date) {
        let now = new Date();
        let today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        let day_count = parseInt((today - from_date) / (24 * 60 * 60 * 1000)) + 1;
        let day_offset = from_date.getDay();
        let from_date_ts = from_date.getTime();

        let row_properties = [];
        for (let i = 0; i < day_count; i++) {
            let row_index = parseInt((i + day_offset - this.WEEKDAY_OFFSET) / 7);
            let timestamp = from_date_ts + (i * (24 * 60 * 60 * 1000));
            let working_date = new Date(timestamp);
            while (row_index >= row_properties.length) {
                row_properties.push({
                    year_at_start: working_date.getFullYear(),
                    month_at_start: working_date.getMonth(),
                    days: [],
                });
            }

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
            row_properties[row_index].days.push(td);
        }

        return row_properties;
    }

    build_vertical_table(from_date, first_date) {
        /* Create the dom table */
        let year_table = crel('table', { class: "year-table" });
        let row_properties = this.build_row_data(from_date, first_date);
        row_properties.reverse();

        // Create a new row for the weekday labels,
        // The first column is a usually empty column that may contain a month label
        let first_month_label = crel('td',
            {
                "class": "month-label",
                "rowspan": 2
            },
            this.MONTHS[row_properties[0].month_at_start]
        );
        year_table.insertBefore(crel('tr', first_month_label), year_table.firstChild);
        for (let i = 0; i < 7; i++) {
            year_table.firstChild.appendChild(crel('th', this.WEEKDAYS[(i + this.WEEKDAY_OFFSET) % 7]));
        }

        for (let i = 0; i < row_properties.length; i++) {
            let current_row = row_properties[i];
            let row_element = crel('tr');
            let buffer = null;
            if (i == row_properties.length - 1) {
                if (i > 0) {
                    if (current_row.month_at_start == row_properties[i - 1].month_at_start) {
                        buffer = crel('td');
                    }
                } else {
                    // only one row, label was set before loop
                }
            } else {
                if (current_row.month_at_start != row_properties[i + 1].month_at_start) {
                    if (current_row.month_at_start == 0) {
                        buffer = crel('td');
                    } else {
                        buffer = crel('td',
                            {
                                "class": "month-label",
                                "rowspan": 2
                            },
                            this.MONTHS[row_properties[i + 1].month_at_start]
                        );
                    }
                } else {
                    if (i > 0) {
                        if (current_row.month_at_start == row_properties[i - 1].month_at_start) {
                            buffer = crel('td');
                        }
                    }
                }
            }

            if (buffer) {
                row_element.appendChild(buffer);
            }

            if (i > 0) {
                for (let j = current_row.days.length; j < 7; j++) {
                    row_element.appendChild(crel('td'));
                }
            }

            for (let j = 0; j < current_row.days.length; j++) {
                row_element.appendChild(current_row.days[j]);
            }
            if (i > 0 && current_row.year_at_start != row_properties[i - 1].year_at_start) {
                year_table.appendChild(
                    crel('tr',
                        crel('td', 
                            {
                                "class": "month-label",
                                "rowspan": 2
                            },
                            this.MONTHS[11]
                        ),
                        crel('td',
                            {
                                'colspan': 7,
                                'class': 'year-delim'
                            },
                            crel('span',
                                crel('hr'),
                                crel('div',
                                    current_row.year_at_start
                                ),
                                crel('hr')
                            )
                        )
                    )
                )
            }
            year_table.appendChild(row_element);
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

