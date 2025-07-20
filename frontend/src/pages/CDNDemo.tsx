import React, { useEffect } from 'react';
import { CDNImage, CDNAvatar, CDNBackgroundImage, CDNPicture } from '@/components/cdn/CDNImage';
import { preloadAssets, configureCDNCaching } from '@/config/cdn';

/**
 * Demo page showing CDN usage examples
 * This page demonstrates various CDN optimization techniques
 */
const CDNDemo: React.FC = () => {
  useEffect(() => {
    // Configure CDN caching on mount
    configureCDNCaching();

    // Preload critical assets
    preloadAssets([
      'logo.png',
      'hero-background.jpg',
      'fonts/inter-var.woff2',
    ]);
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">CDN Configuration Demo</h1>

      {/* Basic CDN Image */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Basic CDN Image</h2>
        <div className="grid gap-4">
          <CDNImage
            src="agents/nexus-avatar.jpg"
            alt="NEXUS Agent"
            width={400}
            height={300}
            className="rounded-lg shadow-lg"
          />
          <p className="text-sm text-muted-foreground">
            Automatically optimized with WebP/AVIF format and responsive srcset
          </p>
        </div>
      </section>

      {/* Avatar Examples */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Avatar Components</h2>
        <div className="flex gap-4 items-center">
          <CDNAvatar src="user-avatar.jpg" alt="User" size="sm" />
          <CDNAvatar src="user-avatar.jpg" alt="User" size="md" />
          <CDNAvatar src="user-avatar.jpg" alt="User" size="lg" />
          <CDNAvatar src="user-avatar.jpg" alt="User" size="xl" />
        </div>
      </section>

      {/* Background Image */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Background Image with Overlay</h2>
        <CDNBackgroundImage
          src="hero-fitness.jpg"
          className="h-64 rounded-lg overflow-hidden"
          overlay
        >
          <div className="flex items-center justify-center h-full text-white">
            <div className="text-center">
              <h3 className="text-3xl font-bold mb-2">GENESIS NGX</h3>
              <p className="text-lg">Optimized background images with CDN</p>
            </div>
          </div>
        </CDNBackgroundImage>
      </section>

      {/* Responsive Picture Element */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Art Direction with Picture Element</h2>
        <CDNPicture
          sources={[
            {
              media: '(max-width: 640px)',
              src: 'hero-mobile.jpg',
              format: 'webp',
            },
            {
              media: '(max-width: 1024px)',
              src: 'hero-tablet.jpg',
              format: 'webp',
            },
          ]}
          fallbackSrc="hero-desktop.jpg"
          alt="Responsive hero image"
          className="w-full rounded-lg"
        />
      </section>

      {/* Grid of Agent Avatars */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Agent Gallery</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {[
            { id: 'nexus', name: 'NEXUS' },
            { id: 'blaze', name: 'BLAZE' },
            { id: 'sage', name: 'SAGE' },
            { id: 'spark', name: 'SPARK' },
            { id: 'wave', name: 'WAVE' },
            { id: 'luna', name: 'LUNA' },
            { id: 'stella', name: 'STELLA' },
            { id: 'nova', name: 'NOVA' },
          ].map((agent) => (
            <div key={agent.id} className="text-center">
              <CDNImage
                src={`agents/${agent.id}.jpg`}
                alt={`${agent.name} Agent`}
                width={150}
                height={150}
                className="rounded-full mx-auto mb-2"
                quality={90}
              />
              <p className="font-medium">{agent.name}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Performance Metrics */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">CDN Performance Benefits</h2>
        <div className="bg-muted rounded-lg p-6">
          <h3 className="font-semibold mb-4">Optimization Features:</h3>
          <ul className="space-y-2">
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span>Automatic WebP/AVIF format selection based on browser support</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span>Responsive srcset generation for optimal image sizes</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span>Lazy loading with priority preloading for critical images</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span>Cache busting with version parameters</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span>Service Worker integration for offline caching</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span>Environment-based CDN URLs (production/staging/development)</span>
            </li>
          </ul>
        </div>
      </section>

      {/* Code Examples */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Usage Examples</h2>
        <div className="bg-muted rounded-lg p-6">
          <pre className="text-sm overflow-x-auto">
{`// Basic image with CDN optimization
<CDNImage 
  src="product.jpg" 
  alt="Product" 
  width={800} 
  height={600}
/>

// Avatar with size presets
<CDNAvatar 
  src="user.jpg" 
  alt="User" 
  size="lg" 
/>

// Background image with overlay
<CDNBackgroundImage 
  src="hero.jpg" 
  overlay
>
  <h1>Content over image</h1>
</CDNBackgroundImage>

// Art direction for responsive
<CDNPicture
  sources={[
    { media: '(max-width: 640px)', src: 'mobile.jpg' },
    { media: '(max-width: 1024px)', src: 'tablet.jpg' }
  ]}
  fallbackSrc="desktop.jpg"
  alt="Responsive image"
/>`}
          </pre>
        </div>
      </section>
    </div>
  );
};

export default CDNDemo;