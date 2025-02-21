"use client"

import React, { useState, useEffect } from 'react';
import Image from "next/image";
import {showToast} from "@/app/toast";
import {ToastContainer} from "react-toastify";
import {API_URL} from "@/app/constants";
// 定义对象的类型
interface Item {
  file: string;
  storyboards: object[];
}

export default function AIImageGenerator() {
    const [storyboardDatas, setStoryboardDatas] = useState<Item[]>([]);
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
        fetch(API_URL + 'api/novel/initial')
            .then(response => response.json())
            .then(data => {
//                 setFragments(data || []);
                setStoryboardDatas(data || []);
                console.log(storyboardDatas)
                setLoaded(true);
            })
            .catch(error => {
                console.error('Error initializing data:', error);
                setLoaded(false);
            });
    };

    const extractStoryboard = () => {
        setStoryboardDatas([])
        showToast('开始生成');
        fetch(API_URL + 'api/save/novel/storyboard')
            .then(response => response.json())
            .then(data => {
            initialize()
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

            const response = await fetch(API_URL + 'api/update/novel/storyboard', {
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

    const fanyi = async (index:number, storyboardIndex:number, itemIndex:number, desc: string) => {
        console.log(desc)
        try {
            const response = await fetch(API_URL + 'api/prompt/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({"content":desc}),
            })

            const translateRes = await response.json()
            const newStoryboardDatas = [...storyboardDatas];
            newStoryboardDatas[index].storyboards[storyboardIndex].storyboard[itemIndex].prompts = translateRes["en"];
            setStoryboardDatas(newStoryboardDatas);
            showToast("成功");
        } catch (error) {
            showToast("失败");
            console.error('Failed to generate random description:', error)
        }
    }

    const generateAllImages = () => {
        setImages([]);
        showToast('开始生成，请等待');
        fetch(API_URL + 'api/novel/images', {
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
        fetch(API_URL + 'api/novel/images')
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

    const generateSingleImage = async (index:number, storyboardIndex:number, itemIndex:number, prompts: string) => {
        try {
            showToast('开始');
            const response = await fetch(API_URL + 'api/novel/image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: index + "-" + storyboardIndex + "-" + itemIndex,
                    content: prompts,
                    outdir: "storyboard/"
                }),
            });
            if (!response.ok) {
                throw new Error('Failed to regenerate image');
            }
            const data = await response.json();
            const imageUrl = data.url;
            const url = addCacheBuster(`http://localhost:1198${imageUrl}`);
            const newStoryboardDatas = [...storyboardDatas];
            newStoryboardDatas[index].storyboards[storyboardIndex].storyboard[itemIndex].storyboard_image = imageUrl;
            setStoryboardDatas(newStoryboardDatas);
            saveStoryboard(index, storyboardIndex, itemIndex, "storyboard_image", imageUrl)
            console.log(`successfully regenerate image for prompt ${name}.`);
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
                        <button onClick={generateAllImages} className="generate-all">一键生图</button>
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
                    {storyboardDatas.map((storyboardData, index) => (
                        storyboardData.storyboards.map((storyboardObj, storyboardIndex) => (
                        <tr>
                            <td>
                              <span>{storyboardData.file}</span>
                            </td>
                            <td>
                              <span>{storyboardObj.text}</span>
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
                            {storyboardObj.storyboard.map((storyboard, itemIndex)=>(
                               <tr>
                                   <td><span>{storyboard.storyboard_index}</span></td>
                                   <td width="300">
                                       <textarea
                                            value={storyboardDatas[index].storyboards[storyboardIndex].storyboard[itemIndex].storyboard_text} rows={4} className="scrollable"
                                            onChange={(e) => {
                                              const newStoryboardDatas = [...storyboardDatas];
                                              newStoryboardDatas[index].storyboards[storyboardIndex].storyboard[itemIndex].storyboard_text = e.target.value;
                                              setStoryboardDatas(newStoryboardDatas);
                                            }}
                                       ></textarea>
                                       <button onClick={() => fanyi(index, storyboardIndex, itemIndex, storyboard.storyboard_text)}>翻译</button>
                                       <button onClick={() => saveStoryboard(storyboardData.file, storyboardObj.index, storyboard.storyboard_index, "storyboard_text", storyboard.storyboard_text)}>保存</button>
                                   </td>
                                   <td>
                                        <textarea
                                           value={storyboardDatas[index].storyboards[storyboardIndex].storyboard[itemIndex].prompts || ''}
                                           placeholder="prompt"
                                           onChange={(e) => {
                                               const newStoryboardDatas = [...storyboardDatas];
                                                newStoryboardDatas[index].storyboards[storyboardIndex].storyboard[itemIndex].prompts = e.target.value;
                                                setStoryboardDatas(newStoryboardDatas);
                                           }}
                                           rows={4}
                                           className="scrollable"
                                       ></textarea>
                                       <button onClick={() => generateSingleImage(index, storyboardIndex, itemIndex, storyboard.prompts)}>生图</button>
                                       <button onClick={() => saveStoryboard(storyboardData.file, storyboardObj.index, storyboard.storyboard_index, "prompts", storyboard.prompts)}>保存</button>
                                   </td>
                                   <td>
                                       <textarea
                                          value={storyboardDatas[index].storyboards[storyboardIndex].storyboard[itemIndex].negative_prompts || ''}
                                          placeholder="prompt"
                                          onChange={(e) => {
                                              const newStoryboardDatas = [...storyboardDatas];
                                               newStoryboardDatas[index].storyboards[storyboardIndex].storyboard[itemIndex].negative_prompts = e.target.value;
                                               setStoryboardDatas(newStoryboardDatas);
                                          }}
                                          rows={4}
                                          className="scrollable"
                                      ></textarea>
                                      <button onClick={() => saveStoryboard(storyboardData.file, storyboardObj.index, storyboard.storyboard_index, "negative_prompts", storyboard.negative_prompts)}>保存</button>
                                   </td>
                                   <td>
                                    <textarea
                                         value={storyboardDatas[index].storyboards[storyboardIndex].storyboard[itemIndex].storyboard_subtitle || ''}
                                         placeholder="prompt"
                                         onChange={(e) => {
                                             const newStoryboardDatas = [...storyboardDatas];
                                              newStoryboardDatas[index].storyboards[storyboardIndex].storyboard[itemIndex].storyboard_subtitle = e.target.value;
                                              setStoryboardDatas(newStoryboardDatas);
                                         }}
                                         rows={4}
                                         className="scrollable"
                                     ></textarea>
                                     <button onClick={() => saveStoryboard(storyboardData.file, storyboardObj.index, storyboard.storyboard_index, "storyboard_subtitle", storyboard.storyboard_subtitle)}>保存</button>
                                    </td>
                                   <td>
                                    {storyboard.storyboard_image ?
                                           (<img width="100" src={API_URL + storyboard.storyboard_image}/>)
                                   : ""}
                                       <button onClick={() => saveStoryboard(storyboardData.file, storyboardObj.index, storyboard.storyboard_index, "storyboard_image", storyboard.storyboard_image)}>保存</button>
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