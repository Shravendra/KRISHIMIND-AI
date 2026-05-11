/* KrishiMind-AI Logo Component
   A stylized leaf-brain fusion representing intelligent farming
*/
export function Logo({ size = 40, showText = true, variant = 'default' }) {
  const isLight = variant === 'light'
  const textColor = isLight ? 'text-white' : 'text-leaf-800'
  const subColor = isLight ? 'text-leaf-200' : 'text-leaf-600'

  return (
    <div className="flex items-center gap-2.5 select-none">
      {/* SVG Mark */}
      <svg
        width={size}
        height={size}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="flex-shrink-0"
      >
        {/* Outer leaf shape */}
        <path
          d="M24 4C14 4 6 12 6 22C6 32 14 44 24 44C34 44 42 32 42 22C42 12 34 4 24 4Z"
          fill={isLight ? 'rgba(255,255,255,0.15)' : '#dcfce7'}
        />
        {/* Main leaf */}
        <path
          d="M24 8C17 8 10 15 10 24C10 31 15 39 24 42C33 39 38 31 38 24C38 15 31 8 24 8Z"
          fill={isLight ? 'rgba(255,255,255,0.25)' : '#86efac'}
        />
        {/* Leaf center gradient overlay */}
        <path
          d="M24 10C18 10 12 17 12 25C12 31 16 38 24 41C32 38 36 31 36 25C36 17 30 10 24 10Z"
          fill="#16a34a"
          opacity="0.9"
        />
        {/* Neural network nodes */}
        <circle cx="24" cy="19" r="2.5" fill="white" opacity="0.95"/>
        <circle cx="18" cy="25" r="2" fill="white" opacity="0.9"/>
        <circle cx="30" cy="25" r="2" fill="white" opacity="0.9"/>
        <circle cx="20" cy="31" r="1.8" fill="white" opacity="0.85"/>
        <circle cx="28" cy="31" r="1.8" fill="white" opacity="0.85"/>
        {/* Neural connections */}
        <line x1="24" y1="19" x2="18" y2="25" stroke="white" strokeWidth="1.2" opacity="0.7"/>
        <line x1="24" y1="19" x2="30" y2="25" stroke="white" strokeWidth="1.2" opacity="0.7"/>
        <line x1="18" y1="25" x2="20" y2="31" stroke="white" strokeWidth="1.2" opacity="0.7"/>
        <line x1="30" y1="25" x2="28" y2="31" stroke="white" strokeWidth="1.2" opacity="0.7"/>
        <line x1="18" y1="25" x2="28" y2="31" stroke="white" strokeWidth="0.8" opacity="0.4"/>
        <line x1="30" y1="25" x2="20" y2="31" stroke="white" strokeWidth="0.8" opacity="0.4"/>
        {/* Stem */}
        <path
          d="M24 42 L24 46"
          stroke={isLight ? '#86efac' : '#15803d'}
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        {/* Tiny sprout leaves on stem */}
        <path
          d="M24 44 Q21 42 20 40"
          stroke={isLight ? '#86efac' : '#15803d'}
          strokeWidth="1.5"
          strokeLinecap="round"
          fill="none"
        />
        <path
          d="M24 44 Q27 42 28 40"
          stroke={isLight ? '#86efac' : '#15803d'}
          strokeWidth="1.5"
          strokeLinecap="round"
          fill="none"
        />
      </svg>

      {showText && (
        <div className="flex flex-col leading-none">
          <span className={`font-display font-bold tracking-tight ${textColor}`}
                style={{ fontSize: size * 0.45 }}>
            KrishiMind AI
          </span>
          <span className={`font-body font-medium tracking-widest uppercase ${subColor}`}
                style={{ fontSize: size * 0.26 }}>
            Agri Intelligence
          </span>
        </div>
      )}
    </div>
  )
}

export default Logo
