let daylist = document.querySelector('.days')
let monthName = document.querySelector('.month-name')
let yearName = document.querySelector('.year')
let prev = document.querySelector('.prev')
let next = document.querySelector('.next')
let dateDisplay = document.querySelector('#dateDisplay')


let monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'july', 'August', 'September', 'October', 'November', 'December']
var dt = new Date();
var month = dt.getMonth() + 1;
var year = dt.getFullYear();
var currentDay = dt.getDate();

prev.addEventListener('click', event => {
    if (month === 1) {
        month = 12;
        year -= 1
    } else {
        month = month - 1;
    }
    calander();
})
next.addEventListener('click', event => {
    if (month === 12) {
        month = 1;
        year += 1
    } else {
        month = month + 1;

    }
    calander()
})

const calander = () => {
    daylist.innerHTML = ''
    daysInMonth = new Date(year, month, 0).getDate();
    dayNumber = new Date(year, month - 1, 1).getDay();

    console.log(year, month, monthName, dayNumber)

    monthName.innerHTML = monthNames[month - 1]
    yearName.innerHTML = year;
    dateDisplay.textContent = currentDay

    let gaps;
    if (dayNumber === 0) {
        gaps = 6
        console.log(gaps)
    } else {
        gaps = dayNumber - 1
    }

    for (var day = -gaps + 1; day <= daysInMonth; day++) {
        const days = document.createElement('li')

        if (day <= 0) {
            days.innerHTML = "";
            daylist.appendChild(days);
        } else if (day === currentDay && month === dt.getMonth() + 1 && year === dt.getFullYear()) {
            days.setAttribute('class', 'active');
            days.innerHTML = day;
            daylist.appendChild(days);
        } else {
            days.innerHTML = day;
            daylist.appendChild(days);
        }
    }
}
