function applyLeave(name, email) {
  return {
    user: {
      name: name,
      email: email,
      leave_type: '',
      from_date: '',
      to_date: '',
      no_of_days: '',
      reason: '',
    },
    errors: {},
    isLoading: false,

    validateField(field, regex, errorMessage) {
      if (!regex.test(this.user[field])) {
        this.errors[field] = errorMessage;
      } else {
        this.errors[field] = '';
      }
    },
    validateName() {
      this.validateField('name', /^[a-zA-Z\s]+$/, 'Name must contain only letters and spaces');
    },

    validateLeaveType() {
      const errorMessage = 'Leave Type cannot be empty';
      if (!this.user.leave_type.trim()) {
        this.errors.leave_type = errorMessage;
      } else {
        this.errors.leave_type = '';
      }
    },

    validateFromDate() {
      const currentDate = new Date();
      const selectedDate = new Date(this.user.from_date);

      if (selectedDate < currentDate) {
        this.errors.from_date = 'From Date must be today or later';
      } else {
        this.errors.from_date = '';

        if (this.user.leave_type === 'Planned') {
          const plannedLeaveStartDate = new Date(currentDate);
          plannedLeaveStartDate.setDate(currentDate.getDate() + 10);

          if (selectedDate < plannedLeaveStartDate) {
            this.errors.from_date = 'Planned leave date must be at least 10 days from today';
          }
        }
      }
    },

    validateToDate() {
      const fromDate = new Date(this.user.from_date);
      const selectedDate = new Date(this.user.to_date);

      if (selectedDate < fromDate) {
        this.errors.to_date = 'To Date must be later than or equal to From Date';
      } else {
        this.errors.to_date = '';
      }
    },

    setFormattedDates() {
      const fromDate = new Date(this.user.from_date);
      const toDate = new Date(this.user.to_date);

      this.user.from_date = this.formatDate(fromDate);
      this.user.to_date = this.formatDate(toDate);
    },

    formatDate(date) {
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const day = date.getDate().toString().padStart(2, '0');
      const year = date.getFullYear();
      return `${month}/${day}/${year}`;
    },

    validateNoOfDays() {
      const errorMessage = 'Number of days must be a positive integer and less than or equal to 10';
      const days = parseInt(this.user.no_of_days, 10);

      if (isNaN(days) || days <= 0 || days > 10) {
        this.errors.no_of_days = errorMessage;
      } else {
        this.errors.no_of_days = '';
      }
    },

    validateReason() {
      const errorMessage = 'Reason cannot be empty and should be less than or equal to 50 characters';
      const maxReasonLength = 50;

      if (!this.user.reason.trim() || this.user.reason.length > maxReasonLength) {
        this.errors.reason = errorMessage;
      } else {
        this.errors.reason = '';
      }
    },

    async leaveRequest() {
      this.validateName();
      this.validateLeaveType();
      this.validateFromDate();
      this.validateToDate();
      this.validateNoOfDays();
      this.validateReason();

      if (Object.values(this.errors).some((error) => error !== '')) {
        return;
      }

      this.isLoading = true;

      // set formatted dates before making the API request
      this.setFormattedDates();

      await fetch(API_URL + API_APPLY_LEAVE_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(this.user),
      })
        .then((response) => {
          if (response.ok) {
            return response.json();
          }
          return Promise.reject(response);
        })
        .then((data) => {
          this.isLoading = false;
          window.location.replace(APP_URL + API_MY_LEAVE);
        })
        .catch((err) => {
          this.isLoading = false;
          err.json().then((errdata) => {
            alert(errdata.detail);
          });
        });
    },
  };
}
