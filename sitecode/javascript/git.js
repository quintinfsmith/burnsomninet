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

        let rows = [];
        let weekdays = ['Sun', 'Mon', 'Tue', 'Wed', "Thu", 'Fri', 'Sat'];
        for (let i = 0; i < 7; i++) {
            let row = crel('tr', crel('td', weekdays[i]));
            year_table.appendChild(row);
            rows.push(row);
        }

        for (let i = 0; i < day_offset; i++) {
            rows[i % 7].appendChild(crel('td', { 'class': 'oob' }, crel('div')));
        }


        let day_one_ts = day_one.getTime();
        for (let i = 0; i < day_count; i++) {
            let timestamp = day_one_ts + (i * (24 * 60 * 60 * 1000));
            let working_date = new Date(timestamp);
            let date_string = working_date.getFullYear() + "-";
            if (working_date.getMonth() + 1 < 10) {
                date_string += '0';
            }
            date_string += (working_date.getMonth() + 1) + "-";
            if (working_date.getDate() < 10) {
                date_string += '0';
            }
            date_string += working_date.getDate();

            let td = crel('td',
                {
                    'data-date': date_string,
                    'class': (working_date.getMonth() % 2 == 0 ? "evenmonth" : "")
                },
                crel('div'));
            this.commit_block_elements[(new_year * 366) + i] = td;
            rows[(i + day_offset) % 7].appendChild(td);
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
