'use client'

import React, {useEffect, useState} from 'react'
import Image from "next/image";
import {showToast} from "@/app/toast";
import {ToastContainer} from "react-toastify";


export default function RolesExtractor() {
    const [roles, setRoles] = useState<Record<string, object>>({})
    const [isLoading, setIsLoading] = useState(false)

    useEffect(() => {
        showToast("提取本地角色");
        extractRoles(true);
    }, []);

    const addCacheBuster = (url: string) => {
        const cacheBuster = `?v=${Date.now()}`
        return url.includes('?') ? `${url}&${cacheBuster}` : `${url}${cacheBuster}`
    }

    const extractRoles = async (isLocal: boolean) => {
        setIsLoading(true)
        try {
            const endpoint = isLocal
                ? 'http://localhost:1198/api/novel/characters/local'
                : 'http://localhost:1198/api/novel/characters'
            const response = await fetch(endpoint)
            const data = await response.json()
            if (response.status == 40401) {
                showToast("本地没有角色");
                return
            }
            setRoles(data)
        } catch (error) {
            showToast("失败");
            console.error('Failed to extract roles:', error)
        } finally {
            setIsLoading(false)
        }
    }

    const handleRoleChange = (roleName: string, content: string, type: string) => {
        const newRole = roles[roleName]
        newRole[type] = content

        setRoles(prev => ({
            ...prev,
            [roleName]: newRole
        }))
    }

    const fanyi = async (roleName:string, desc: string) => {
        console.log(desc)
        try {
            const response = await fetch('http://localhost:1198/api/prompt/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({"content":desc}),
            })

            const translateRes = await response.json()

            const newRole = roles[roleName]
            newRole["prompts"] = translateRes["en"]

            setRoles(prev => ({
                ...prev,
                [roleName]: newRole
            }))

            showToast("成功");
        } catch (error) {
            showToast("失败");
            console.error('Failed to generate random description:', error)
        }
    }

    const generateSingleImage = async (roleName:string, prompts: string) => {
        try {
            showToast('开始');
            const response = await fetch('http://localhost:1198/api/novel/image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: roleName,
                    content: prompts,
                    outdir: 'role/'
                }),
            });
            if (!response.ok) {
                throw new Error('Failed to regenerate image');
            }
            const data = await response.json();
            const imageUrl = data.url;
            const url = addCacheBuster(`http://localhost:1198${imageUrl}`);
            handleRoleChange(roleName, url, "imgUrl")
            console.log(`successfully regenerate image for prompt ${name}.`);
            showToast('成功');
        } catch (error) {
            console.error('Error saving attachment:', error);
            showToast('失败');
        }
    }

    const generateRandomDescription = async (roleName: string) => {
        try {
            const response = await fetch('http://localhost:1198/api/novel/characters/random')
            const randomDescription = await response.json()
            setEditedDescriptions(prev => ({
                ...prev,
                [roleName]: randomDescription
            }))
            showToast("成功");
        } catch (error) {
            showToast("失败");
            console.error('Failed to generate random description:', error)
        }
    }

    const saveChanges = async () => {
        setIsLoading(true)
        try {
            const response = await fetch('http://localhost:1198/api/novel/characters', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(roles),
            })

            console.log("response", response)
//             setRoles(prev => {
//                 const newRoles = { ...prev }
//                 Object.entries(editedDescriptions).forEach(([name, description]) => {
//                     if (newRoles[name]) {
//                         newRoles[name] = description
//                     }
//                 })
//                 return newRoles
//             })
            showToast("成功");
        } catch (error) {
            showToast("失败");
            console.error('Failed to save changes:', error)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div style={{
            fontFamily: 'Arial, sans-serif',
            maxWidth: '100%',
            margin: '0 auto',
            padding: '20px',
            backgroundColor: '#f7f7f7',
            borderRadius: '8px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}>
            <h1 style={{
                textAlign: 'center',
                marginBottom: '20px',
                color: '#000000'
            }}>生成中文prompts之后提取里面的角色，用于文生图时锁定人物</h1>
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                gap: '10px',
                marginBottom: '20px'
            }}>
                <button
                    onClick={() => extractRoles(true)}
                    disabled={isLoading}
                    style={{
                        padding: '10px 20px',
                        fontSize: '16px',
                        backgroundColor: '#1a1a1a',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer',
                        transition: 'background-color 0.3s'
                    }}
                >
                    {isLoading ? '加载中...' : '提取本地描述'}
                </button>
                <button
                    onClick={() => extractRoles(false)}
                    disabled={isLoading}
                    style={{
                        padding: '10px 20px',
                        fontSize: '16px',
                        backgroundColor: '#1a1a1a',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer',
                        transition: 'background-color 0.3s'
                    }}
                >
                    {isLoading ? '加载中...' : '提取角色'}
                </button>
            </div>
            <table style={{
               border: '1px solid #bdc3c7',
               borderRadius: '5px',
               backgroundColor: 'white'
           }}>
                <tr>
                    <th class="fixed-width">角色</th>
                    <th>描述</th>
                    <th>Prompts</th>
                    <th>角色图</th>
                </tr>
            {Object.entries(roles).map(([name, roleInfo]) => (
                <tr>
                    <td>{name}</td>
                    <td><textarea
                        value={roleInfo["desc"]}
                        onChange={(e) => handleRoleChange(name, e.target.value, "desc")}
                        style={{
                            width: '100%',
                            minHeight: '20px',
                            padding: '10px',
                            borderRadius: '5px',
                            backgroundColor: '#f8f8f8',
                            color: '#000000',
                            fontSize: '14px',
                        }}
                    /><button onClick={() => fanyi(name, roleInfo["desc"])}
                      style={{
                          padding: '5px 10px',
                          fontSize: '14px',
                          backgroundColor: '#1a1a1a',
                          color: 'white',
                          border: 'none',
                          borderRadius: '5px',
                          cursor: 'pointer',
                          transition: 'background-color 0.3s'
                      }}
                    >
                      翻译
                    </button>
                    </td>
                    <td><textarea
                        value={roleInfo["prompts"]}
                        onChange={(e) => handleRoleChange(name, e.target.value, "prompts")}
                        style={{
                            width: '100%',
                            minHeight: '20px',
                            padding: '10px',
                            borderRadius: '5px',
                            backgroundColor: '#f8f8f8',
                            color: '#000000',
                            fontSize: '14px',
                        }}
                    />
                    <button
                        onClick={() => generateSingleImage(name, roleInfo["prompts"])}
                        style={{
                            padding: '5px 10px',
                            fontSize: '14px',
                            backgroundColor: '#1a1a1a',
                            color: 'white',
                            border: 'none',
                            borderRadius: '5px',
                            cursor: 'pointer',
                            transition: 'background-color 0.3s'
                        }}
                    >
                        生成角色图
                    </button>
                    </td>
                    <td>
                    {roleInfo["imgUrl"] ? (<img width="100" src={roleInfo["imgUrl"]}/> ) : ""}
                    </td>
                </tr>
            ))}
            </table>
            {Object.keys(roles).length > 0 && (
                <button
                    onClick={saveChanges}
                    disabled={isLoading || Object.keys(roles).length === 0}
                    style={{
                        padding: '10px 20px',
                        fontSize: '16px',
                        backgroundColor: '#1a1a1a',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer',
                        transition: 'background-color 0.3s',
                        display: 'block',
                        margin: '0 auto'
                    }}
                >
                    {isLoading ? '保存中...' : '保存修改'}
                </button>
            )}
            <ToastContainer />
        </div>
    )
}