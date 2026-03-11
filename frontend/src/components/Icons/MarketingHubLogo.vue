<template>
  <svg
    width="300"
    height="300"
    viewBox="0 0 300 300"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <linearGradient id="logo-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#EF4444;stop-opacity:1" />
        <stop offset="100%" style="stop-color:#DC2626;stop-opacity:1" />
      </linearGradient>
    </defs>
    <!-- Rounded background with gradient -->
    <rect
      x="0"
      y="0"
      width="300"
      height="300"
      rx="60"
      fill="url(#logo-gradient)"
    />
    <!-- Megaphone body -->
    <path
      d="M130 110a76 76 0 0 0 51-19c4-2.5 7.5 1.2 7.5 5v76c0 3.8-3.5 7.5-7.5 5a76 76 0 0 0-51-19H84c-5 0-9-4-9-9v-25c0-5 4-9 9-9z"
      fill="white"
      opacity="0.95"
    />
    <!-- Broadcast waves -->
    <g opacity="0.85">
      <path
        d="M206 127c5 0 10 5 10 10v26c0 5-5 10-10 10"
        stroke="white"
        stroke-width="7.5"
        stroke-linecap="round"
        fill="none"
      />
      <path
        d="M229 140v20"
        stroke="white"
        stroke-width="7.5"
        stroke-linecap="round"
      />
    </g>
    <!-- Bottom curve -->
    <path
      d="M94 178c0 18 5 33 14 48 2.5 5 0 11.5-6.5 11.5s-10-5-11.5-9a66 66 0 0 1-1-50"
      fill="white"
      opacity="0.9"
    />
  </svg>
</template>
