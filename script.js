let canvas, ctx, snake, food, direction, gameLoop;
let foodCount = 0;
let selectedDifficulty = 'normal';
const DIFFICULTY_SETTINGS = {
    'easy': { foodTarget: 15, speed: 200 },
    'normal': { foodTarget: 25, speed: 150 },
    'hard': { foodTarget: 10, speed: 100 }
};

let bgMusic;
let isMusicPlaying = false;
let borderAnimation = false;
let borderHue = 0;
let borderAnimationFrame;
let encourageMessage = '';
let encourageTimer = null;

const ENCOURAGE_MESSAGES = [
    "Great job! Keep going! 🎉",
    "You're doing amazing! 🌟",
    "Fantastic snake skills! 🐍",
    "Unstoppable! 💪",
    "You're on fire! 🔥",
    "Incredible moves! ⭐",
    "Keep up the great work! 👏",
    "You're crushing it! 💫"
];

let particles = [];
let celebrationAnimationFrame;

class Particle {
    constructor(x, y, color) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.size = Math.random() * 5 + 2;
        const angle = Math.random() * Math.PI * 2;
        const speed = Math.random() * 8 + 2;
        this.vx = Math.cos(angle) * speed;
        this.vy = Math.sin(angle) * speed;
        this.gravity = 0.1;
        this.life = 255;
        this.alpha = 1;
        this.decay = 2;
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.vy += this.gravity;
        this.life -= this.decay;
        this.alpha = this.life / 255;
        return this.life > 0;
    }

    draw(ctx) {
        ctx.save();
        ctx.globalAlpha = this.alpha;
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    }
}

function celebrate() {
    const colors = ['#FF5252', '#4CAF50', '#FDD835', '#2196F3', '#9C27B0'];
    let celebrationTime = 0;
    const celebrationDuration = 100000;
    const particleInterval = 500;
    let lastParticleTime = 0;
    
    function createParticles() {
        for (let i = 0; i < 15; i++) {
            particles.push(new Particle(0, canvas.height / 2, 
                colors[Math.floor(Math.random() * colors.length)]));
            particles.push(new Particle(canvas.width, canvas.height / 2, 
                colors[Math.floor(Math.random() * colors.length)]));
        }
    }

    function animateCelebration(timestamp) {
        if (!celebrationTime) celebrationTime = timestamp;
        const elapsed = timestamp - celebrationTime;
        
        if (timestamp - lastParticleTime > particleInterval) {
            createParticles();
            lastParticleTime = timestamp;
        }

        ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        particles = particles.filter(particle => {
            const isAlive = particle.update();
            if (isAlive) {
                particle.draw(ctx);
            }
            return isAlive;
        });

        // Draw the win message on top of particles
        drawWinMessage();

        if (elapsed < celebrationDuration) {
            celebrationAnimationFrame = requestAnimationFrame(animateCelebration);
        }
    }

    new Audio('win.mp3').play();
    // stop background music
    toggleMusic();

    createParticles();
    requestAnimationFrame(animateCelebration);
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize audio elements
    bgMusic = document.getElementById('bgMusic');
    
    // Add resize event listener
    window.addEventListener('resize', resizeCanvas);
});

function selectDifficulty(difficulty) {
    selectedDifficulty = difficulty;
    // Update button styles
    document.querySelectorAll('.difficulty-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    document.querySelector(`.${difficulty}`).classList.add('selected');
}

function checkCollision(head) {
    // Start from index 1 to skip the head itself
    for (let i = 1; i < snake.length; i++) {
        if (snake[i].x === head.x && snake[i].y === head.y) {
            return true;  // Collision detected
        }
    }
    return false;
}

function drawSnakeSegment(x, y, isHead) {
    ctx.save();
    
    if (isHead) {
        // Draw larger green head
        let headGradient = ctx.createLinearGradient(x, y, x + 20, y + 20);
        headGradient.addColorStop(0, '#69F0AE');
        headGradient.addColorStop(1, '#388E3C');
        
        ctx.fillStyle = headGradient;
        roundedRect(x - 2, y - 2, 24, 24, 6);
        
        // Add shine effect to head
        ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.beginPath();
        ctx.arc(x + 6, y + 6, 4, 0, Math.PI * 2);
        ctx.fill();
    } else {
        // Draw thinner red body segments
        let bodyGradient = ctx.createLinearGradient(x, y, x + 20, y + 20);
        bodyGradient.addColorStop(0, '#FF5252');
        bodyGradient.addColorStop(1, '#D32F2F');
        
        ctx.fillStyle = bodyGradient;
        roundedRect(x + 2, y + 2, 16, 16, 4);
    }
    
    ctx.restore();
}

// Helper function to draw rounded rectangles
function roundedRect(x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
    ctx.fill();
}

function handleMobileControl(dir) {
    if (dir === 'up' && direction !== 'down') direction = 'up';
    if (dir === 'down' && direction !== 'up') direction = 'down';
    if (dir === 'left' && direction !== 'right') direction = 'left';
    if (dir === 'right' && direction !== 'left') direction = 'right';
}

function generateFood() {
    let newFood;
    do {
        newFood = {
            x: Math.floor(Math.random() * (canvas.width/20)) * 20,
            y: Math.floor(Math.random() * (canvas.height/20)) * 20
        };
    } while (isOnSnake(newFood));  // Keep generating until we find a free spot
    return newFood;
}

function isOnSnake(pos) {
    return snake.some(segment => segment.x === pos.x && segment.y === pos.y);
}

function startGame() {
    // Reset game cover image to original
    document.getElementById('gameCover').src = 'cover.png';
    
    document.getElementById('startBtn').style.display = 'none';
    document.getElementById('gameCover').style.display = 'none';
    document.getElementById('difficultySelect').style.display = 'none';
    document.getElementById('gameCanvas').style.display = 'block';
    
    canvas = document.getElementById('gameCanvas');
    ctx = canvas.getContext('2d');
    
    canvas.width = 400;
    canvas.height = 400;
    
    snake = [{x: 0, y: 0}];
    food = generateFood();  // Use the new function instead of direct assignment
    direction = 'right';
    foodCount = 0;
    
    if (gameLoop) clearInterval(gameLoop);
    gameLoop = setInterval(update, DIFFICULTY_SETTINGS[selectedDifficulty].speed);
    document.addEventListener('keydown', changeDirection);
    
    // Start music when game starts (with error handling)
    if (!isMusicPlaying && bgMusic) {
        toggleMusic();
    }
    
    // Reset border
    canvas.style.border = '2px solid #333';
    borderAnimation = false;
    borderHue = 0;
    
    encourageMessage = '';
    if (encourageTimer) clearTimeout(encourageTimer);
    
    particles = [];
    if (celebrationAnimationFrame) {
        cancelAnimationFrame(celebrationAnimationFrame);
    }
    
    // Hide fail overlay
    document.getElementById('failOverlay').style.display = 'none';
}

function update() {
    const head = {x: snake[0].x, y: snake[0].y};
    
    if (direction === 'right') head.x += 20;
    if (direction === 'left') head.x -= 20;
    if (direction === 'up') head.y -= 20;
    if (direction === 'down') head.y += 20;
    
    if (head.x < 0) head.x = canvas.width - 20;
    if (head.x >= canvas.width) head.x = 0;
    if (head.y < 0) head.y = canvas.height - 20;
    if (head.y >= canvas.height) head.y = 0;
    
    if (checkCollision(head)) {
        gameOver();
        return;
    }
    
    snake.unshift(head);
    
    if (head.x === food.x && head.y === food.y) {
        foodCount++;
        
        // Check if it's a multiple of 10
        if (snake.length % 10 === 0) {
            toggleBorderAnimation(true);
            // Show random encourage message
            encourageMessage = ENCOURAGE_MESSAGES[Math.floor(Math.random() * ENCOURAGE_MESSAGES.length)];
            // Clear any existing timer
            if (encourageTimer) clearTimeout(encourageTimer);
            // Clear message after 3 seconds
            encourageTimer = setTimeout(() => {
                encourageMessage = '';
            }, 3000);
            setTimeout(() => toggleBorderAnimation(false), 3000);
        }
        
        if (foodCount >= DIFFICULTY_SETTINGS[selectedDifficulty].foodTarget) {
            clearInterval(gameLoop);
            toggleBorderAnimation(false);
            
            // Start celebration before showing alert
            celebrate();
            
            // Delay the alert to show celebration for 10 seconds
            setTimeout(() => {
                alert('Congratulations! You won!');
                document.getElementById('startBtn').style.display = 'block';
                document.getElementById('difficultySelect').style.display = 'flex';
                document.getElementById('gameCover').style.display = 'block';
                document.getElementById('gameCanvas').style.display = 'none';
                // Clean up celebration
                cancelAnimationFrame(celebrationAnimationFrame);
                particles = [];
            }, 10000);
            return;
        }
        food = generateFood();
    } else {
        snake.pop();
    }
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw snake with different head and body segments
    snake.forEach((segment, index) => {
        drawSnakeSegment(segment.x, segment.y, index === 0);
    });
    
    // Draw food
    let foodGradient = ctx.createRadialGradient(
        food.x + 10, food.y + 10, 2,
        food.x + 10, food.y + 10, 10
    );
    foodGradient.addColorStop(0, '#FDD835');
    foodGradient.addColorStop(1, '#F57F17');
    
    ctx.fillStyle = foodGradient;
    ctx.beginPath();
    ctx.arc(food.x + 10, food.y + 10, 10, 0, Math.PI * 2);
    ctx.fill();

    // Add snake length display
    ctx.save();
    ctx.fillStyle = '#FF5252';  // Red color to match snake body
    ctx.font = 'bold 20px Arial';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'top';
    ctx.shadowColor = 'rgba(0,0,0,0.5)';
    ctx.shadowBlur = 4;
    ctx.fillText(`Length: ${snake.length}`, canvas.width - 10, 10);
    ctx.restore();

    // Draw encourage message if exists
    if (encourageMessage) {
        ctx.save();
        ctx.fillStyle = '#4CAF50';
        ctx.font = 'bold 24px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.shadowColor = 'rgba(0,0,0,0.5)';
        ctx.shadowBlur = 4;
        ctx.fillText(encourageMessage, canvas.width / 2, canvas.height / 2);
        ctx.restore();
    }
}

function changeDirection(event) {
    if (event.key === 'ArrowUp' && direction !== 'down') direction = 'up';
    if (event.key === 'ArrowDown' && direction !== 'up') direction = 'down';
    if (event.key === 'ArrowLeft' && direction !== 'right') direction = 'left';
    if (event.key === 'ArrowRight' && direction !== 'left') direction = 'right';
}

// Update canvas size based on screen width
function resizeCanvas() {
    const canvas = document.getElementById('gameCanvas');
    const maxWidth = Math.min(320, window.innerWidth * 0.95);
    canvas.style.width = maxWidth + 'px';
    canvas.style.height = maxWidth + 'px';
}



// Modify the gameOver function
function gameOver() {
    clearInterval(gameLoop);
    toggleBorderAnimation(false);
    if (isMusicPlaying) {
        toggleMusic();
    }
    
    

    window.location.href = 'fail.html';
    
    encourageMessage = '';
    if (encourageTimer) clearTimeout(encourageTimer);
}

function toggleMusic() {
    if (!bgMusic) return; // Guard clause in case audio isn't available
    
    const musicBtn = document.getElementById('musicToggle');
    if (isMusicPlaying) {
        bgMusic.pause();
        musicBtn.textContent = '🔇';
    } else {
        bgMusic.play().catch(e => {
            console.log('Audio play failed:', e);
            musicBtn.textContent = '🔇';
            return;
        });
        musicBtn.textContent = '🔈';
    }
    isMusicPlaying = !isMusicPlaying;
}

// Add this function to handle the rainbow border animation
function animateRainbowBorder() {
    if (!borderAnimation) return;
    
    borderHue = (borderHue + 1) % 360;
    canvas.style.border = `2px solid hsl(${borderHue}, 100%, 50%)`;
    borderAnimationFrame = requestAnimationFrame(animateRainbowBorder);
}

// Add this function to start/stop the border animation
function toggleBorderAnimation(start) {
    borderAnimation = start;
    if (start) {
        animateRainbowBorder();
    } else {
        cancelAnimationFrame(borderAnimationFrame);
        canvas.style.border = '2px solid #333';
    }
}

// Add this function to draw the win message
function drawWinMessage() {
    ctx.save();
    
    // Draw background glow
    ctx.shadowColor = '#4CAF50';
    ctx.shadowBlur = 20;
    ctx.fillStyle = 'rgba(76, 175, 80, 0.2)';
    ctx.fillRect(0, canvas.height/2 - 50, canvas.width, 100);
    
    // Draw main text
    ctx.fillStyle = '#4CAF50';
    ctx.font = 'bold 40px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.shadowColor = 'rgba(0,0,0,0.5)';
    ctx.shadowBlur = 4;
    ctx.fillText('Congratulations!', canvas.width/2, canvas.height/2 - 25);
    ctx.fillText('You Win! 🏆', canvas.width/2, canvas.height/2 + 25);
    
    ctx.restore();
}