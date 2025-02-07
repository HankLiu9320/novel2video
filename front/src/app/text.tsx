'use client'

import { useState, useEffect } from 'react'

export default function TextEditor() {
  const [novelContent, setNovelContent] = useState('')
  const [novelMessage, setNovelMessage] = useState('')

  useEffect(() => {
    loadContent('novel')
  }, [])

  const loadContent = async (type: 'novel') => {
    try {
      const response = await fetch(`http://localhost:1198/api/${type}/load`)
      if (response.ok) {
        const data = await response.json()
        if (data.content) {
          setNovelContent(data.content)
          setMessage(type, '内容已加载')
        } else {
          setNovelContent('')
          setMessage(type, '没有找到保存的内容')
        }
      } else {
        throw new Error('加载失败')
      }
    } catch (error) {
      setMessage(type, '加载失败，请稍后重试。')
    }
  }

  const handleSave = async (type: 'novel') => {
    try {
      const content = novelContent
      const response = await fetch(`http://localhost:1198/api/${type}/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
      })

      if (response.ok) {
        setMessage(type, '保存成功！')
      } else {
        throw new Error('保存失败')
      }
    } catch (error) {
      setMessage(type, '保存失败，请稍后重试。')
    }
  }

  const setMessage = (type: 'novel', message: string) => {
    setNovelMessage(message)
  }

  return (
    <div className="max-w-full mx-auto my-10 px-4 py-6 bg-gray-100 rounded-lg shadow-lg">
      <div className="mb-8 bg-gray-50 p-4 rounded-lg">
        <h2 className="text-3xl font-bold text-center mb-4 text-black border-b-2 border-gray-300 pb-2">小说</h2>
        <textarea
          value={novelContent}
          onChange={(e) => setNovelContent(e.target.value)}
          placeholder="在这里输入小说文本..."
          className="w-full min-h-[400px] p-4 mb-4 border border-gray-400 rounded-md text-gray-800 bg-white resize-vertical focus:outline-none focus:ring-2 focus:ring-gray-500 text-lg"
        />
        <button
          onClick={() => handleSave('novel')}
          className="w-full py-3 bg-gray-900 text-white border-none rounded-md cursor-pointer text-lg hover:bg-gray-900 transition-colors"
        >
          保存小说
        </button>
        {novelMessage && (
          <p className={`text-center mt-4 ${novelMessage.includes('成功') ? 'text-gray-800' : 'text-gray-600'}`}>
            {novelMessage}
          </p>
        )}
      </div>
    </div>
  )
}