document.addEventListener('DOMContentLoaded', function() {
    particlesJS("particles-js", {
        "particles": {
            "number": { "value": 90, "density": { "enable": true, "value_area": 500 } },
            "color": { "value": "#4f9da6" }, // Cor do seu tema
            "shape": { "type": "circle" },
            "opacity": { "value": 0.5, "random": false },
            "size": { "value": 5, "random": true },
            "line_linked": { 
                "enable": true, 
                "distance": 150, 
                "color": "#3a7bd5", // Azul para contraste
                "opacity": 0.3,
                "width": 1 
            },
            "move": { 
                "enable": true, 
                "speed": 2, 
                "direction": "none", 
                "random": true, 
                "out_mode": "out" 
            }
        },
        "interactivity": {
            "detect_on": "canvas",
            "events": {
                "onhover": {
                    "enable": true, // Ativa a interação com o mouse
                    "mode": "repulse" // Faz as partículas fugirem
                },
                "onclick": {
                    "enable": true,
                    "mode": "push" // Adiciona partículas ao clicar
                }
            },
            "modes": {
                "repulse": {
                    "distance": 100, // Distância da fuga (em pixels)
                    "duration": 0.4 // Tempo da animação (em segundos)
                },
                "push": {
                    "particles_nb": 4 // Quantidade de partículas criadas ao clicar
                }
            }
        }
    });
});