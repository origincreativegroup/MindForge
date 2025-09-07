import React from 'react'

// Renders annotations at specified positions
export default function AnnotationLayer({ annotations }) {
  return (
    <>
      {annotations.map((a, idx) => (
        <div key={idx} className="annotation" style={{ left: a.x, top: a.y }}>
          {a.text}
        </div>
      ))}
    </>
  )
}
