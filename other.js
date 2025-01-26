let left = document.getElementById("left");
let desc = document.getElementById("desc");
let list = document.getElementById("list");
let right = document.getElementById("right");
let descriptor = document.getElementById("descM");
let trending = ["Toyota Corolla 2024", "Toyota Camry 2024", "Toyota Prius 2024"];
let descript = ["Comfortable cabin with spacious seating and automatic climate control. Includes advanced safety features. Fuel efficient with an estimated 35 Miles Per Gallon. Connectivity included with 8-inch touchscreen display compatible with Apple CarPlay and Android Auto", "Comfortable ride with spacious interior. Variety of safety features with safety sensors and multiple alerts. Fuel efficient ranging from 22-39 MPG gas-powered. Upwards of 53 MPG for Hybrid models. Connectivity for Apple and Android included", "Safety features include emergency braking, lane departure alert, and more. Fuel efficiency with up to 56 MPG on the highway. Modern design with sleek lines and contoured body. Efficiently designed LED headlights. Connectivity for Apple and Android included."];
let position = 0;
let prevPos = 0;
let index = 0;
let width = 660;
function go(event) {
    
}
desc.textContent = trending[0];
descriptor.textContent = descript[0];
left.addEventListener('click', go);
right.addEventListener('click', go);
left.addEventListener('click', (event) => {
    position+=width;
    position = Math.min(0, position);
    if(Math.abs(position-prevPos) != 0) {
        index--;
        prevPos = position;
        event.preventDefault()
    
        desc.animate({
            opacity: [0, 1]
        }, 700).onfinish = () => desc.style.opacity = 1
        descriptor.animate({
            opacity: [0, 1]
        }, 700).onfinish = () => descriptor.style.opacity = 1

    }
    
    desc.textContent = trending[index];
    descriptor.textContent = descript[index];

    list.style.marginLeft = position + 'px';

});
right.addEventListener('click', (event) => {
    position-=width;
    position = Math.max(-1320, position);
    if(Math.abs(position-prevPos) != 0) {
        index++;
        prevPos = position;
        event.preventDefault()
    
        desc.animate({
            opacity: [0, 1]
        }, 700).onfinish = () => desc.style.opacity = 1
        descriptor.animate({
            opacity: [0, 1]
        }, 700).onfinish = () => descriptor.style.opacity = 1
    }
    
    list.style.marginLeft = position + 'px';
    desc.textContent = trending[index];
    descriptor.textContent = descript[index];
    console.log("CLICKED");

});
