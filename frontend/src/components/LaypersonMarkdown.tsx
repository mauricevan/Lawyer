import Markdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import styles from "./LaypersonMarkdown.module.css";

interface Props {
  children: string;
  className?: string;
}

export function LaypersonMarkdown({ children, className }: Props) {
  return (
    <div className={className ? `${styles.markdown} ${className}` : styles.markdown}>
      <Markdown rehypePlugins={[rehypeRaw]}>{children}</Markdown>
    </div>
  );
}
