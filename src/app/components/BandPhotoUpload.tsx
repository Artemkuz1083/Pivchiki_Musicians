import React, { useState, useRef } from 'react'
import { groupService } from '../../api/BandService'
import { Camera, Loader2, Image as ImageIcon, CheckCircle2 } from 'lucide-react'

interface PhotoUploadProps {
    groupId: number;
    currentPhotoUrl?: string;
    onUploadSuccess: (newUrl: string) => void;
}

export default function GroupPhotoUpload({ groupId, currentPhotoUrl, onUploadSuccess }: PhotoUploadProps) {
    const [preview, setPreview] = useState<string | null>(currentPhotoUrl || null)
    const [uploading, setUploading] = useState(false)
    const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle')
    const fileInputRef = useRef<HTMLInputElement>(null)

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return

        // 1. Делаем локальное превью для юзера
        const objectUrl = URL.createObjectURL(file)
        setPreview(objectUrl)
        setUploading(true)
        setStatus('idle')

        try {
    const data = await groupService.uploadGroupMedia(groupId, file)
    
    // Проверяем все возможные варианты, откуда взять ссылку на фото
    const verifiedUrl = data?.PhotoURL || data?.photoURL || data?.url || data?.Link;

    if (verifiedUrl) {
        setStatus('success')
        setPreview(verifiedUrl)
        onUploadSuccess(verifiedUrl)
    } else {
        // Если бэк возвращает пустой ответ или просто { message: "ok" }, 
        // но фотку сохраняет, нам придется завязаться на локальное превью
        setStatus('success')
        onUploadSuccess(objectUrl) // передаем созданную браузером временную ссылку blob:
    }
} catch (error) {
    console.error('Ошибка при загрузке медиа:', error)
    setStatus('error')
}
    }

    const triggerFileInput = () => {
        fileInputRef.current?.click()
    }

    return (
        <div className="flex flex-col items-center justify-center p-6 bg-white rounded-3xl border border-gray-100 shadow-sm max-w-sm mx-auto">
            <div
                onClick={triggerFileInput}
                className="relative w-32 h-32 rounded-full cursor-pointer group bg-gray-50 border-2 border-dashed border-gray-200 hover:border-[#60519B] flex items-center justify-center overflow-hidden transition-all"
            >
                {preview ? (
                    <img
                        src={preview}
                        alt="Preview"
                        className={`w-full h-full object-cover transition-opacity ${uploading ? 'opacity-40' : 'opacity-100'}`}
                    />
                ) : (
                    <div className="text-center p-4">
                        <ImageIcon className="w-8 h-8 text-gray-400 mx-auto mb-1 group-hover:text-[#60519B] transition-colors" />
                        <span className="text-xs text-gray-400 font-medium block">Добавить фото</span>
                    </div>
                )}

                {/* Оверлей при наведении */}
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity rounded-full">
                    <Camera className="w-6 h-6 text-white" />
                </div>

                {/* Лоадер в процессе загрузки */}
                {uploading && (
                    <div className="absolute inset-0 bg-black/20 flex items-center justify-center rounded-full">
                        <Loader2 className="w-8 h-8 text-[#60519B] animate-spin" />
                    </div>
                )}
            </div>

            {/* Скрытый инпут */}
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept="image/jpeg,image/png"
                className="hidden"
            />

            {/* Статус-сообщения */}
            <div className="mt-4 text-center">
                {status === 'success' && (
                    <p className="text-emerald-600 text-sm font-semibold flex items-center gap-1">
                        <CheckCircle2 className="w-4 h-4" /> Фото успешно обновлено!
                    </p>
                )}
                {status === 'error' && (
                    <p className="text-red-500 text-sm font-medium">
                        Не удалось загрузить. Попробуйте еще раз.
                    </p>
                )}
                {status === 'idle' && !uploading && (
                    <p className="text-gray-400 text-xs">
                        Поддерживаются форматы JPG, PNG. Макс. размер 5MB.
                    </p>
                )}
            </div>
        </div>
    )
}