from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import os
# from dotenv import load_dotenv

# Load environment variables
# load_dotenv()

# Define difficulty levels
DIFFICULTY = {
    'easy': 10,
    'normal': 25,
    'hard': 50
}

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html_part1 = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Snake Game</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
            <style>
                body {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #1a1a1a;
                    font-family: Arial, sans-serif;
                }
                canvas { 
                    border: 2px solid #333;
                    border-radius: 8px;
                    display: none;
                    background-color: #fff;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    max-width: 95vw;  /* Limit width to 95% of viewport width */
                    height: auto;     /* Maintain aspect ratio */
                }
                #startBtn {
                    padding: 15px 40px;
                    font-size: 24px;
                    cursor: pointer;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    transition: all 0.3s ease;
                }
                #startBtn:hover {
                    background-color: #45a049;
                    transform: translateY(-2px);
                }
                .game-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 20px;
                    width: 100%;
                    padding: 10px;
                    box-sizing: border-box;
                }
                .controls {
                    display: grid;
                    grid-template-areas:
                        '. up .'
                        'left down right';
                    grid-template-columns: repeat(3, 60px);
                    gap: 10px;
                    margin-top: 20px;
                }
                .control-btn {
                    width: 60px;
                    height: 60px;
                    border: none;
                    border-radius: 50%;
                    background-color: #4CAF50;
                    color: white;
                    font-size: 24px;
                    cursor: pointer;
                    touch-action: manipulation;
                    user-select: none;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }
                .control-btn:active {
                    transform: translateY(2px);
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }
                .btn-up { grid-area: up; }
                .btn-down { grid-area: down; }
                .btn-left { grid-area: left; }
                .btn-right { grid-area: right; }
                @media (min-width: 768px) {
                    .controls {
                        display: none;
                    }
                }
                .author {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    color: #4CAF50;
                    font-size: 16px;
                    font-family: Arial, sans-serif;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                }
                .game-cover {
                    width: 280px;
                    height: 280px;
                    margin-bottom: 20px;
                    border-radius: 15px;
                    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
                    object-fit: cover;
                }

                @media (max-width: 320px) {
                    .game-cover {
                        width: 95vw;
                        height: auto;
                    }
                }
                .difficulty-select {
                    display: flex;
                    gap: 15px;
                    margin: 20px 0;
                    justify-content: center;
                }
                .difficulty-btn {
                    padding: 10px 25px;
                    font-size: 18px;
                    cursor: pointer;
                    border: none;
                    border-radius: 15px;
                    color: white;
                    transition: all 0.3s ease;
                }
                .easy { background-color: #4CAF50; }
                .normal { background-color: #FFA500; }
                .hard { background-color: #FF4444; }
                .difficulty-btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }
                .difficulty-btn.selected {
                    box-shadow: 0 0 0 3px #fff, 0 0 0 6px currentColor;
                }
                .music-control {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: rgba(76, 175, 80, 0.8);
                    padding: 10px;
                    border-radius: 50%;
                    cursor: pointer;
                    width: 40px;
                    height: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 20px;
                    border: none;
                    transition: all 0.3s ease;
                }
                .music-control:hover {
                    transform: scale(1.1);
                    background: rgba(76, 175, 80, 1);
                }
            </style>
        </head>
        <body>
            <audio id="bgMusic" loop>
                <source src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>
            <button class="music-control" id="musicToggle" onclick="toggleMusic()">🎵</button>
            
            <div class="game-container">
                <!-- from internet url image-->
                <img src="https://cdn.pixabay.com/photo/2013/07/13/13/42/snake-161424_1280.png" 
                     alt="Snake Game Cover" 
                     class="game-cover"
                     id="gameCover"
                     style="max-width: 100%; height: auto;">
                <div class="difficulty-select" id="difficultySelect">
                    <button class="difficulty-btn easy" onclick="selectDifficulty('easy')">Easy</button>
                    <button class="difficulty-btn normal selected" onclick="selectDifficulty('normal')">Normal</button>
                    <button class="difficulty-btn hard" onclick="selectDifficulty('hard')">Hard</button>
                </div>
                <button id="startBtn" onclick="startGame()">Start Game</button>
                <canvas id="gameCanvas" width="320" height="320"></canvas>
                <div class="controls">
                    <button class="control-btn btn-up" onclick="handleMobileControl('up')">up</button>
                    <button class="control-btn btn-left" onclick="handleMobileControl('left')">left</button>
                    <button class="control-btn btn-down" onclick="handleMobileControl('down')">down</button>
                    <button class="control-btn btn-right" onclick="handleMobileControl('right')">right</button>
                </div>
            </div>
            <div class="author">Author: Pan</div>
            
            <script>
                let canvas, ctx, snake, food, direction, gameLoop;
                let foodCount = 0;
                let selectedDifficulty = 'normal';
                const DIFFICULTY_SETTINGS = {
                    'easy': { foodTarget: 10, speed: 200 },
                    'normal': { foodTarget: 25, speed: 150 },
                    'hard': { foodTarget: 50, speed: 100 }
                };

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
                    
                    // Start music when game starts
                    if (!isMusicPlaying) {
                        toggleMusic();
                    }
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
                        if (foodCount >= DIFFICULTY_SETTINGS[selectedDifficulty].foodTarget) {
                            clearInterval(gameLoop);
                            alert('Congratulations! You won!');
                            document.getElementById('startBtn').style.display = 'block';
                            document.getElementById('difficultySelect').style.display = 'flex';
                            document.getElementById('gameCover').style.display = 'block';
                            document.getElementById('gameCanvas').style.display = 'none';
                            return;
                        }
                        food = generateFood();  // Use the new function here too
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

                // Add resize event listener
                window.addEventListener('resize', resizeCanvas);

                function gameOver() {
                    clearInterval(gameLoop);
                    // Stop music on game over
                    if (isMusicPlaying) {
                        toggleMusic();
                    }
                    alert('Game Over! Snake hit itself!');
                    document.getElementById('startBtn').style.display = 'block';
                    document.getElementById('difficultySelect').style.display = 'flex';
                    document.getElementById('gameCover').style.display = 'block';  // Show cover again
                    document.getElementById('gameCanvas').style.display = 'none';
                }

                let bgMusic = document.getElementById('bgMusic');
                let isMusicPlaying = false;
                
                function toggleMusic() {
                    const musicBtn = document.getElementById('musicToggle');
                    if (isMusicPlaying) {
                        bgMusic.pause();
                        // use emoji
                        musicBtn.textContent = '🔇';
                    } else {
                        bgMusic.play().catch(e => console.log('Audio play failed:', e));
                        // use emoji
                        musicBtn.textContent = '🔈';

                    }
                    isMusicPlaying = !isMusicPlaying;
                }
            </script>
        </body>
        </html>
        """
        
        self.wfile.write(html_part1.encode())

def find_free_port():
    # Try ports from 8080 to 8099
    for port in range(8080, 8100):
        try:
            # Test if port is available
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise OSError("No free ports found in range 8080-8099")

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    port = find_free_port()
    server_address = ('', port)
    try:
        httpd = server_class(server_address, handler_class)
        # set address reuse
        httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(f"Server started on port {port}")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server")
        # close httpd right now
        httpd.server_close()
        httpd.socket.close()

if __name__ == "__main__":
    run()

