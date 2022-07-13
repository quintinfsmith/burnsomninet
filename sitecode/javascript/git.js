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
        this.year_elements = {};
        this.commit_block_elements = {};
        this.element_wrapper = crel('div');
        this.element_title = crel('div');
        this.element.appendChild(this.element_title);
        this.element.appendChild(crel('div', this.element_wrapper));

        let now = new Date();

        let from_date = new Date(now.getFullYear(), 0, 1);
        let to_date = new Date(now.getFullYear() + 1, 0, 1);
        let url = "/api/git/commits" +
            "?project=" + options.project +
            "&datefrom=" + (from_date.getTime() / 1000) +
            "&dateto=" + (to_date.getTime() / 1000);

        api_call(url,
            function(response) {
                let year = (new Date()).getFullYear();
                if (response.length == 0) {
                    this.new_year_table(year);
                }
                this.update_commits(response);
                this.show_year(year);
            }.bind(this),
            function(response) {
                console.log(response);
            }
        );

    }

    show_year(year) {
        if (this.year_elements[year]) {
            for (let k in this.year_elements) {
                this.year_elements[k].style.display = "none";
            }
            this.year_elements[year].style.display = "inline-block";
            this.set_title("Git Activity in " + year);
        }
    }

    set_title(title) {
        this.element_title.innerText = title;
    }

    new_year_table(new_year) {
        let year_table = crel('table', { class: "year-table" });
        let day_one = new Date(new_year, 0, 1);
        let day_offset = (day_one).getDay();
        let day_count = 365;
        // Leap Year?
        if (new Date(new_year, 1, 29).getMonth() == 1) {
            day_count += 1;
        }

        let weekdays = ['Sun', 'Mon', 'Tue', 'Wed', "Thu", 'Fri', 'Sat'];
        year_table.appendChild(crel('tr'));
        for (let i = 0; i < 14; i++) {
            year_table.lastChild.appendChild(crel('th', weekdays[i % 7]));
        }

        year_table.appendChild(crel('tr'));
        for (let i = 0; i < day_offset; i++) {
            year_table.lastChild.appendChild(crel('td', { 'class': 'oob' }, crel('div')));
        }

        let day_one_ts = day_one.getTime();
        for (let i = 0; i < day_count; i++) {
            let timestamp = day_one_ts + (i * (24 * 60 * 60 * 1000));
            let working_date = new Date(timestamp);
            let date_string = build_simple_date_string(working_date);

            let td = crel('td',
                {
                    'data-date': date_string,
                    'class': (working_date.getMonth() % 2 == 0 ? "evenmonth" : "")
                },
                crel('div')
            );

            this.commit_block_elements[(new_year * 366) + i] = td;

            if ((i + day_offset) % 14 == 0) {
                year_table.appendChild(crel('tr'));
            }

            year_table.lastChild.appendChild(td);
        }


        // Insert new table
        let added = false;
        let existing_years = Object.keys(this.year_elements);
        existing_years.sort();

        for (let i = 0; i < existing_years; i++) {
            let working_year = existing_years[i];
            if (new_year < working_year) {
                this.element_wrapper.insertBefore(
                    year_table,
                    this.year_elements[working_year]
                );
                added = true;
                break;
            }
        }

        if (! added) {
            this.element_wrapper.appendChild(year_table);
        }

        this.year_elements[new_year] = year_table;
    }

    update_commits(new_commits) {
        for (let i = 0; i < new_commits.length; i++) {
            let commit = new_commits[i];
            let date = new Date(commit.date * 1000);
            let working_year = date.getFullYear();
            if (! this.year_elements[working_year]) {
                this.new_year_table(working_year);
            }

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

        this.element.appendChild(this.element_clone);
        this.element.appendChild(this.element_url);

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

