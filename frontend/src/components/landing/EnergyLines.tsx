
import React, { useEffect, useRef } from 'react';

export const EnergyLines: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const lines: Array<{
      x1: number;
      y1: number;
      x2: number;
      y2: number;
      opacity: number;
      speed: number;
    }> = [];

    // Create energy lines
    for (let i = 0; i < 5; i++) {
      lines.push({
        x1: Math.random() * canvas.width,
        y1: Math.random() * canvas.height,
        x2: Math.random() * canvas.width,
        y2: Math.random() * canvas.height,
        opacity: Math.random() * 0.3 + 0.1,
        speed: Math.random() * 0.5 + 0.2,
      });
    }

    let animationId: number;

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      lines.forEach((line, index) => {
        const gradient = ctx.createLinearGradient(line.x1, line.y1, line.x2, line.y2);
        gradient.addColorStop(0, `rgba(59, 130, 246, ${line.opacity})`);
        gradient.addColorStop(0.5, `rgba(147, 51, 234, ${line.opacity * 1.5})`);
        gradient.addColorStop(1, `rgba(59, 130, 246, ${line.opacity})`);

        ctx.strokeStyle = gradient;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(line.x1, line.y1);
        ctx.lineTo(line.x2, line.y2);
        ctx.stroke();

        // Animate the lines
        line.x1 += Math.sin(Date.now() * 0.001 + index) * line.speed;
        line.y1 += Math.cos(Date.now() * 0.001 + index) * line.speed;
        line.x2 += Math.sin(Date.now() * 0.001 + index + Math.PI) * line.speed;
        line.y2 += Math.cos(Date.now() * 0.001 + index + Math.PI) * line.speed;

        // Wrap around screen
        if (line.x1 < 0) line.x1 = canvas.width;
        if (line.x1 > canvas.width) line.x1 = 0;
        if (line.y1 < 0) line.y1 = canvas.height;
        if (line.y1 > canvas.height) line.y1 = 0;
        if (line.x2 < 0) line.x2 = canvas.width;
        if (line.x2 > canvas.width) line.x2 = 0;
        if (line.y2 < 0) line.y2 = canvas.height;
        if (line.y2 > canvas.height) line.y2 = 0;
      });

      animationId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 pointer-events-none opacity-40"
    />
  );
};
