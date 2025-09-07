import { useEffect, useRef } from 'react'

// Simple hook that manages a WebSocket connection and emits incoming messages
export default function useWebSocket(url, onMessage) {
  const socketRef = useRef(null)

  useEffect(() => {
    const socket = new WebSocket(url)
    socketRef.current = socket
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (err) {
        console.error('Failed to parse message', err)
      }
    }
    return () => socket.close()
  }, [url, onMessage])

  return socketRef
}
