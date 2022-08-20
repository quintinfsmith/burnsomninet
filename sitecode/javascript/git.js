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

        if (options.orientation && options.orientation == 'horizontal') {
            this.element.classList.add('horizontal');
            this.element_table = this.build_horizontal_table(day_one, first_date);
        } else {
            this.element_table = this.build_vertical_table(day_one, first_date);
        }

        this.element_wrapper = crel('div',
            { "class": "table-wrapper"},
            this.element_table
        );

        this.element_title = crel('div',
            { "class": "title" },
            "Git activity"
        );
        this.element.appendChild(this.element_title);
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

    build_week_data(from_date, first_date) {
        let now = new Date();
        let today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        let day_count = parseInt((today - from_date) / (24 * 60 * 60 * 1000)) + 1;
        let day_offset = from_date.getDay();
        let from_date_ts = from_date.getTime();

        let index_bump = 0;
        if (Math.floor((day_offset - this.WEEKDAY_OFFSET) / 7) < 0) {
            index_bump = 1;
        }

        let week_properties = [];
        for (let i = 0; i < day_count; i++) {
            let week_index = Math.floor((i + day_offset - this.WEEKDAY_OFFSET) / 7) + index_bump;
            let timestamp = from_date_ts + (i * (24 * 60 * 60 * 1000));
            let working_date = new Date(timestamp);

            while (week_index >= week_properties.length) {
                week_properties.push({
                    year_at_start: working_date.getFullYear(),
                    month_at_start: working_date.getMonth(),
                    days: [],
                });
            }

            let date_string = build_simple_date_string(working_date);
            let doy = working_date.getTime() - (new Date(working_date.getFullYear(), 0, 1));
            doy = parseInt(doy / (1000 * 60 * 60 * 24));

            let td = crel('td',
                {
                    'data-date': date_string,
                    'class': (working_date.getMonth() % 2 == 0 ? "evenmonth" : "")
                },
                crel('div')
            );

            this.commit_block_elements[(working_date.getFullYear() * 366) + doy] = td;
            week_properties[week_index].days.push(td);
        }
        return week_properties;
    }

    build_vertical_table(from_date, first_date) {
        /* Create the dom table */
        let year_table = crel('table', { class: "year-table" });
        let week_properties = this.build_week_data(from_date, first_date);
        week_properties.reverse();

        // Create a new row for the weekday labels,
        // The first column is a usually empty column that may contain a month label
        let first_month_label = crel('td',
            {
                "class": "month-label",
                "rowspan": 2
            },
            this.MONTHS[week_properties[0].month_at_start]
        );
        year_table.insertBefore(crel('tr', first_month_label), year_table.firstChild);
        for (let i = 0; i < 7; i++) {
            year_table.firstChild.appendChild(crel('th', this.WEEKDAYS[(i + this.WEEKDAY_OFFSET) % 7]));
        }

        let flag_month_labelled = true;
        let flag_month_changed = false;
        for (let i = 0; i < week_properties.length; i++) {
            let current_week = week_properties[i];
            let row_element = crel('tr');
            let buffer = null;

            let is_december_next = i < week_properties.length - 1 && week_properties[i + 1].month_at_start == 11;
            let different_month_next = i < week_properties.length -1 && current_week.month_at_start != week_properties[i + 1].month_at_start;
            if (flag_month_labelled) {
                flag_month_changed = different_month_next;
                flag_month_labelled = false;
            } else if (flag_month_changed || different_month_next) {
                if (! is_december_next) {
                    buffer = crel('td',
                        {
                            "class": "month-label",
                            "rowspan": 2
                        },
                        this.MONTHS[week_properties[i + 1].month_at_start]
                    );
                } else {
                    buffer = crel('td');
                }
                flag_month_labelled = true;
                flag_month_changed = false;
            } else {
                buffer = crel('td');
            }

            if (buffer) {
                row_element.appendChild(buffer);
            }

            if (i > 0) {
                for (let j = current_week.days.length; j < 7; j++) {
                    row_element.appendChild(crel('td'));
                }
            }

            for (let j = 0; j < current_week.days.length; j++) {
                row_element.appendChild(current_week.days[j]);
            }

            if (i > 0 && current_week.year_at_start != week_properties[i - 1].year_at_start) {
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
                                    current_week.year_at_start
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

    build_horizontal_table(from_date, first_date) {
        /* Create the dom table */
        let year_table = crel('table', { class: "year-table" });
        let week_properties = this.build_week_data(from_date, first_date);
        week_properties.reverse();

        let rows = [];
        for (let i = 0; i < 7; i++) {
            let row = crel('tr');
            //let row = crel('tr', crel('td', this.WEEKDAYS[(i + this.WEEKDAY_OFFSET) % 7]));
            year_table.appendChild(row);
            rows.push(row);
        }

        let month_spans = {};
        for (let i = 0; i < week_properties.length; i++) {
            let week = week_properties[i];
            if (! month_spans[week.year_at_start]) {
                month_spans[week.year_at_start] = {};
            }
            if (! month_spans[week.year_at_start][week.month_at_start]) {
                month_spans[week.year_at_start][week.month_at_start] = 0;
            }
            month_spans[week.year_at_start][week.month_at_start] += 1;
            if (i == 0) {
                month_spans[week.year_at_start][week.month_at_start] += 1;
            }

            for (let j = 0; j < 7; j++) {
                let cell = week.days[j];
                let pushpoint = j;

                // Insert day cells from the bottom-up at end
                if (i == week_properties.length - 1) {
                    pushpoint = (pushpoint + (7 - week.days.length)) % 7;
                }

                if (cell) {
                    rows[pushpoint].appendChild(cell);
                } else {
                    rows[pushpoint].appendChild(crel('td'));
                }
            }
        }

        let header_row = crel('tr');
        let i = 0;
        while (i < week_properties.length) {
            let year = week_properties[i].year_at_start;
            let month = week_properties[i].month_at_start;
            header_row.appendChild(
                crel('th',
                    { colspan: month_spans[year][month] },
                    this.MONTHS[month]
                )
            );
            i += month_spans[year][month];
        }
        year_table.insertBefore(header_row, year_table.firstChild);

        return year_table;
    }

    update_commits(new_commits) {
        /* Add a list of new commits to the widget. Update the table cells accordingly */
        for (let i = 0; i < new_commits.length; i++) {
            let commit = new_commits[i];
            let date = new Date(commit.date * 1000);
            let date_day_start = new Date(date.getFullYear(), date.getMonth(), date.getDate());

            let working_year = date.getFullYear();

            let day_one = new Date(working_year, 0, 1);
            let one_day = 1000 * 60 * 60 * 24;

            let doy = Math.floor((date_day_start.getTime() - day_one.getTime()) / one_day);
            let key = (366 * working_year) + doy;

            let element_td = this.commit_block_elements[key];

            // TODO: figure out why element_td doesn't exist on jul31
            if (! element_td) {
                continue;
            }

            let commit_counts;
            if (element_td && element_td.getAttribute('data-counts')) {
                commit_counts = JSON.parse(element_td.getAttribute('data-counts'));
            } else {
                commit_counts = {};
            }

            let commit_group_name = commit['group'];
            if (!commit_group_name) {
                commit_group_name = "";
            }

            if (!commit_counts[commit_group_name]) {
                commit_counts[commit_group_name] = 0;
            }

            commit_counts[commit_group_name] += 1;
            element_td.setAttribute('data-counts', JSON.stringify(commit_counts));
            let title = "";
            if (Object.keys(commit_counts).length > 1) {
                title = element_td.getAttribute("data-date") + ":\n";
                for (let k in commit_counts) {
                    title += commit_counts[k] + " commit";
                    if (commit_counts[k] != 1) {
                        title += "s";
                    }
                    title += " to " + k + "\n";
                }
                title = title.substr(0, title.length - 1);
            } else {
                title = commit_counts[commit_group_name] + " commit";
                if (commit_counts[commit_group_name] != 1) {
                    title += "s";
                }
                if (commit_group_name) {
                    title += " to " + commit_group_name;
                }
                title += " on " + element_td.getAttribute('data-date');
            }
            element_td.setAttribute('title', title);
            element_td.classList.add('active');

            this.commits.push[commit];
        }
    }
}


class CloneButtonWidget extends SlugWidget {
    constructor(element, options) {
        super(element, options);
        this.url = 'https://' + location.hostname + '/git/' + options.project;
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

