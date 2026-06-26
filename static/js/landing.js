// ============================================
// Demo Search Typewriter
// ============================================

const demoInput = document.getElementById("demo-search");

const questions = [

    "Where is Backpropagation taught?",

    "Explain Gradient Descent.",

    "What is Perceptron?",

    "How does CNN work?",

    "Explain Vanishing Gradient.",

    "What is Multi Layer Perceptron?",

    "Difference between ANN and CNN?",

    "Explain Forward Propagation.",

    "What is Binary Cross Entropy?",

    "How does Backpropagation work?"

];

let questionIndex = 0;

let charIndex = 0;

let deleting = false;

function typeWriter(){

    const current = questions[questionIndex];

    if(!deleting){

        demoInput.value = current.substring(0,charIndex++);

        if(charIndex > current.length){

            deleting = true;

            setTimeout(typeWriter,1800);

            return;

        }

    }

    else{

        demoInput.value = current.substring(0,charIndex--);

        if(charIndex < 0){

            deleting = false;

            questionIndex++;

            if(questionIndex >= questions.length){

                questionIndex = 0;

            }

        }

    }

    setTimeout(typeWriter,deleting ? 18 : 45);

}

typeWriter();


// ============================================
// Popular Search Animation
// ============================================

const chips = document.querySelectorAll(".examples span");

let chipIndex = 0;

setInterval(()=>{

    chips.forEach(chip=>{

        chip.classList.remove("active-chip");

    });

    chips[chipIndex].classList.add("active-chip");

    chipIndex++;

    if(chipIndex>=chips.length){

        chipIndex=0;

    }

},2500);


// ============================================
// Scroll Reveal
// ============================================

const reveals = document.querySelectorAll(

    ".feature-card,.workflow-card,.trust-item,.cta-card"

);

const observer = new IntersectionObserver(

(entries)=>{

    entries.forEach(entry=>{

        if(entry.isIntersecting){

            entry.target.classList.add("active");

        }

    });

},

{

    threshold:.18

}

);

reveals.forEach(el=>{

    el.classList.add("reveal");

    observer.observe(el);

});


// ============================================
// Smooth Get Started Transition
// ============================================

const startButtons = document.querySelectorAll(".primary-btn");

startButtons.forEach(button=>{

    button.addEventListener("click",(e)=>{

        if(button.getAttribute("href")!=="/search") return;

        e.preventDefault();

        document.body.classList.add("fade-out");

        setTimeout(()=>{

            window.location="/search";

        },500);

    });

});


// ============================================
// Background Parallax
// ============================================

const circle1 = document.querySelector(".circle-1");

const circle2 = document.querySelector(".circle-2");

if (circle1 && circle2 && window.matchMedia("(pointer: fine)").matches) {

    document.addEventListener("mousemove",(e)=>{

        const x = e.clientX/window.innerWidth;

        const y = e.clientY/window.innerHeight;

        circle1.style.transform =

            `translate(${x*35}px,${y*35}px)`;

        circle2.style.transform =

            `translate(${-x*30}px,${-y*30}px)`;

    });

}





// ============================================
// Hero Fade
// ============================================

window.addEventListener("load",()=>{

    document.body.classList.add("loaded");

});