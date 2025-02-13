"use client"

import React, { useState, useEffect } from 'react';
import Image from "next/image";
import {showToast} from "@/app/toast";
import {ToastContainer} from "react-toastify";

export default function AIImageGenerator() {
    const [images, setImages] = useState<string[]>([]);
    const [fragments, setFragments] = useState<string[]>([]);
    const [prompts, setPrompts] = useState<string[]>([]);
    const [loaded, setLoaded] = useState<boolean>(false);
    const [promptsEn, setPromptsEn] = useState<string[]>([]);
    const [isLoading] = useState<boolean>(false);

    useEffect(() => {
        initialize();
    }, []);

    const addCacheBuster = (url: string) => {
        const cacheBuster = `?v=${Date.now()}`
        return url.includes('?') ? `${url}&${cacheBuster}` : `${url}${cacheBuster}`
  }

    const initialize = () => {
        fetch('http://localhost:1198/api/novel/initial')
            .then(response => response.json())
            .then(data => {
                setFragments(data || []);
                setLoaded(true);
            })
            .catch(error => {
                console.error('Error initializing data:', error);
                setLoaded(false);
            });
    };

    const extractStoryboard = () => {
        setPrompts([]);
        showToast('开始生成');
        fetch('http://localhost:1198/api/save/novel/storyboard')
            .then(response => response.json())
            .then(data => {
            setPrompts(data || []);
            console.log('Prompts fetched successfully');
        })
        .catch(error => {
            console.error('Error fetching prompts:', error);
            showToast('失败');
        });
    };

    const saveStoryboard = async (fileName, paragraphIdx, storyboardIdx, type, content) => {
        console.log(fileName, paragraphIdx, storyboardIdx, type, content)

        try {

            const response = await fetch('http://localhost:1198/api/update/novel/storyboard', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fileName: fileName,
                    paragraphIdx: paragraphIdx,
                    storyboardIdx: storyboardIdx,
                    type: type,
                    content: content
                })
            });

            if (!response.ok) {
                throw new Error('Failed to save fragments');
            }
            console.log('Fragments saved successfully');
        } catch (error) {
            console.error('Error saving fragments:', error);
        }
    };

    const generateAllImages = () => {
        setImages([]);
        showToast('开始生成，请等待');
        fetch('http://localhost:1198/api/novel/images', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
        })
            .then(response => response.json())
            .then(() => {
                console.log('Images generation initiated');
                refreshImages();
            })
            .catch(error => {
                showToast('失败，请检查日志');
                console.error('Error generating all images:', error)
            });
    };

    type ImageMap = Record<string, string>;

    const refreshImages = () => {
        fetch('http://localhost:1198/api/novel/images')
            .then(response => response.json() as Promise<ImageMap>)
            .then((imageMap: ImageMap) => {
                const updatedImages = [...images];
                for (const [index, imageUrl] of Object.entries(imageMap)) {
                    const numericIndex = Number(index);
                    if (!isNaN(numericIndex)) {
                        updatedImages[numericIndex] = addCacheBuster(`http://localhost:1198${imageUrl}`);
                    }
                }
                setImages(updatedImages);
            })
            .catch(error => console.error('Error fetching image:', error));
    };

    const mergeFragments = (index: number, direction: 'up' | 'down') => {
        if ((direction === 'up' && index === 0) || (direction === 'down' && index === fragments.length - 1)) {
            return;
        }

        const newFragments = [...fragments];
        const newImages = [...images];
        const newPrompts = [...prompts]
        const newPromptsEn = [...promptsEn]

        if (direction === 'up') {
            newFragments[index - 1] += ' ' + newFragments[index];
            newFragments.splice(index, 1);
            newImages.splice(index, 1);
            newPrompts.splice(index, 1)
            newPromptsEn.splice(index, 1)
        } else if (direction === 'down') {
            newFragments[index] += ' ' + newFragments[index + 1];
            newFragments.splice(index + 1, 1);
            newImages.splice(index + 1, 1);
            newPrompts.splice(index+1, 1)
            newPromptsEn.splice(index+1, 1)
        }

        setFragments(newFragments);
        setImages(newImages);
        setPromptsEn(prompts)
        setPrompts(prompts)
        // todo 是不是最好都重新保存一下
        saveFragments(newFragments);
    };

    const saveFragments = async (fragments: string[]) => {
        try {
            const response = await fetch('http://localhost:1198/api/save/novel/fragments', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(fragments),
            });

            if (!response.ok) {
                throw new Error('Failed to save fragments');
            }
            console.log('Fragments saved successfully');
        } catch (error) {
            console.error('Error saving fragments:', error);
        }
    };

    const generateSingleImage = async (index:number) => {
        try {
            showToast('开始');
            const updatedImages = [...images];
            updatedImages[index] = "http://localhost:1198/images/placeholder.png";
            const response = await fetch('http://localhost:1198/api/novel/image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    index: index,
                    content: promptsEn[index]
                }),
            });
            if (!response.ok) {
                throw new Error('Failed to regenerate image');
            }
            const data = await response.json();
            const imageUrl = data.url;
            updatedImages[index] = addCacheBuster(`http://localhost:1198${imageUrl}`);
            setImages(updatedImages);
            console.log(`successfully regenerate image for prompt ${index}.`);
            showToast('成功');
        } catch (error) {
            console.error('Error saving attachment:', error);
            showToast('失败');
        }
    }

    const savePromptEn = async (index: number) => {
        try {
            const response = await fetch('http://localhost:1198/api/novel/prompt/en', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    index: index,
                    content: promptsEn[index]
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to save attachment');
            }
            console.log(`Attachment for fragment ${index + 1} saved successfully.`);
            showToast('保存成功');
        } catch (error) {
            console.error('Error saving attachment:', error);
            showToast('保存失败');
        }
    };

    const savePromptZh = async  (index: number) => {
        try {
            const response = await fetch('http://localhost:1198/api/novel/prompt/zh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    index: index,
                    content: prompts[index]
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to save attachment');
            }
            console.log(`Attachment for fragment ${index + 1} saved successfully.`);
            showToast('保存成功');
        } catch (error) {
            console.error('Error saving attachment:', error);
            showToast('保存失败');
        }
    };

    const generatePromptsEn = async () => {
        try {
            setPromptsEn([]);
            showToast('开始生成，请等待');
            const response = await fetch('http://localhost:1198/api/novel/prompts/en');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setPromptsEn(data || []);
        } catch (error) {
            showToast('失败');
            console.error('Error fetching prompts:', error);
        }
    };


    const generateAudio = () => {
        showToast('开始生成，请等待');
        fetch('http://localhost:1198/api/novel/audio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ fragments })
        })
            .then(response => response.json())
            .then(() => {
                console.log('Audio generation initiated');
            })
            .catch(error => {
                console.error('Error generating audio:', error);
                showToast('失败');
            });
    };

    return (
        <div className="container">
            <div className="button-container">
                <button onClick={extractStoryboard} className="extract-prompts-button">分镜</button>
                {loaded && (
                    <>
                        <button onClick={extractStoryboard} className="extract-prompts-button">分镜</button>
                        <button onClick={generatePromptsEn} className="generate-promptsEn" disabled={isLoading}>
                            {isLoading ? 'Generating...' : '翻译成英文'}
                        </button>
                        <button onClick={generateAllImages} className="generate-all">一键生成</button>
                        <button onClick={initialize} className="refresh-images">刷新</button>
                        <button onClick={generateAudio} className="generate-audio">生成音频</button>
                    </>
                )}
            </div>
            <table style={{
                   border: '1px solid #bdc3c7',
                   borderRadius: '5px',
                   backgroundColor: 'white'
               }}>
                    <tr>
                        <th class="fixed-width">文件</th>
                        <th width="200">段落原文</th>
                        <th>分镜</th>
                    </tr>
            {loaded && (
                <>
                    {fragments.map((line, index) => (
                        line.storyboards.map(item => (
                        <tr>
                            <td>
                              <span>{line.file}</span>
                            </td>
                            <td>
                              <span>{item.text}</span>
                            </td>

                            <td>
                            <table style={{
                               border: '1px solid #bdc3c7',
                               borderRadius: '5px',
                               backgroundColor: 'white'
                            }}>
                            <tr>
                                <th width="50">idx</th>
                                <th width="300">镜头描述</th>
                                <th width="300">Prompts</th>
                                <th width="300">N-prompts</th>
                                <th width="300">字幕</th>
                                <th width="300">图</th>
                            </tr>
                            {item.storyboard.map(storyboard=>(
                               <tr>
                                   <td><span>{storyboard.storyboard_index}</span></td>
                                   <td width="300">
                                       <textarea value={storyboard.storyboard_text} rows={4} className="scrollable"></textarea>
                                       <button onClick={() => saveStoryboard(line.file, item.index, storyboard.storyboard_index, "storyboard_text", storyboard.storyboard_text)}>保存</button>
                                   </td>
                                   <td>
                                        <textarea
                                           value={storyboard.prompts || ''}
                                           placeholder="prompt"
                                           onChange={(e) => {
                                               const newAttachments = [...prompts];
                                               newAttachments[index] = e.target.value;
                                               setPrompts(newAttachments);
                                           }}
                                           rows={4}
                                           className="scrollable"
                                       ></textarea>
                                       <button onClick={() => savePromptZh(index)}>保存</button>
                                   </td>
                                   <td><span>{storyboard.negative_prompts}</span></td>
                                   <td><span>{storyboard.storyboard_subtitle}</span></td>
                                   <td>
                                       <img width="100" src={storyboard.storyboard_image}/>
                                   </td>
                               </tr>
                            ))}
                            </table>
                            </td>
                        </tr>
                        ))
                    ))}
                </>
            )}
            </table>
            <style jsx>{`
                .button-container {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 20px;
                }
                .card {
                    display: flex;
                    justify-content: space-between;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    background-color: #fff;
                }
                .input-section, .prompt-section, .promptEn-section, .image-section {
                    width: 23%;
                }
                textarea {
                    width: 100%;
                    padding: 10px;
                    margin-bottom: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    resize: vertical;
                    overflow-y: auto;
                    color: #333;
                    background-color: #fff;
                }
                .button-group {
                    display: flex;
                    flex-direction: column;
                }
                .button-group .merge-button {
                    margin-bottom: 5px;
                    padding: 5px 10px;
                    font-size: 14px;
                }
                button {
                    background-color: #1a1a1a;
                    color: white;

                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                }
                button:hover {
                    background-color: #333;
                }
                button:disabled {
                    background-color: #ccc;
                    cursor: not-allowed;
                }
                .generate-all, .refresh-images, .generate-promptsEn, .generate-audio {
                    padding: 10px 20px;
                    font-size: 16px;
                }
            `}</style>
            <ToastContainer />
        </div>
    );
}