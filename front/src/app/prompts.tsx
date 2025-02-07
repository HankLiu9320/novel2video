'use client'

import { useState, useEffect } from 'react'

export default function PromptsEditor() {
  const [rolePromptContent, setRolePromptContent] = useState('')
  const [promptContent, setPromptContent] = useState('')
  const [novelMessage, setNovelMessage] = useState('')
  const [promptMessage, setPromptMessage] = useState('')

  useEffect(() => {
    loadContent('role-prompt')
    loadContent('prompt')
  }, [])

  const loadContent = async (type: 'prompt' | 'role-prompt') => {
    try {
      const response = await fetch(`http://localhost:1198/api/${type}/load`)
      if (response.ok) {
        const data = await response.json()
        if (data.content) {
          setMessage(type, '内容已加载')
        } else {
          type === 'prompt' ? setNovelContent('') : setPromptContent('')
          setMessage(type, '没有找到保存的内容')
        }

        if(type === 'role-prompt') {
            setRolePromptContent(data.content)
        } else if(type === 'prompt') {
            setPromptContent(data.content)
        }
      } else {
        throw new Error('加载失败')
      }
    } catch (error) {
      setMessage(type, '加载失败，请稍后重试。')
    }
  }

  const handleSave = async (type: 'role-prompt' | 'prompt') => {
    try {
      const content = type === 'role-prompt' ? rolePromptContent : promptContent
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

  const setMessage = (type: 'novel' | 'prompt', message: string) => {
    type === 'novel' ? setNovelMessage(message) : setPromptMessage(message)
  }

  return (
    <div className="max-w-full mx-auto my-10 px-4 py-6 bg-gray-100 rounded-lg shadow-lg">
    <div className="bg-gray-200 p-4 rounded-lg">
        <h2 className="text-3xl font-bold text-center mb-4 text-black border-b-2 border-gray-400 pb-2">角色提示词</h2>
        <textarea
          value={rolePromptContent}
          onChange={(e) => setRolePromptContent(e.target.value)}
          placeholder="在这里输入提示词..."
          className="w-full min-h-[400px] p-4 mb-4 border border-gray-400 rounded-md text-gray-800 bg-white resize-vertical focus:outline-none focus:ring-2 focus:ring-gray-600 text-lg"
        />
        <button
          onClick={() => handleSave('role-prompt')}
          className="w-full py-3 bg-gray-900 text-white border-none rounded-md cursor-pointer text-lg hover:bg-gray-900 transition-colors"
        >
          保存提示词
        </button>
        {promptMessage && (
          <p className={`text-center mt-4 ${promptMessage.includes('成功') ? 'text-gray-800' : 'text-gray-600'}`}>
            {promptMessage}
          </p>
        )}
      </div>
      <div className="bg-gray-200 p-4 rounded-lg">
        <h2 className="text-3xl font-bold text-center mb-4 text-black border-b-2 border-gray-400 pb-2">画面提示词</h2>
        <textarea
          value={promptContent}
          onChange={(e) => setPromptContent(e.target.value)}
          placeholder="在这里输入提示词..."
          className="w-full min-h-[400px] p-4 mb-4 border border-gray-400 rounded-md text-gray-800 bg-white resize-vertical focus:outline-none focus:ring-2 focus:ring-gray-600 text-lg"
        />
        <button
          onClick={() => handleSave('prompt')}
          className="w-full py-3 bg-gray-900 text-white border-none rounded-md cursor-pointer text-lg hover:bg-gray-900 transition-colors"
        >
          保存提示词
        </button>
        {promptMessage && (
          <p className={`text-center mt-4 ${promptMessage.includes('成功') ? 'text-gray-800' : 'text-gray-600'}`}>
            {promptMessage}
          </p>
        )}
      </div>
    </div>
  )
}